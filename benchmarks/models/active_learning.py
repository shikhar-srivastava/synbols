import numpy as np
import torch
from baal import ModelWrapper
from baal.active import ActiveLearningLoop, get_heuristic
from baal.utils.metrics import ClassificationReport
from torch.nn import CrossEntropyLoss
from torch.utils.data import DataLoader
from torchvision import models


class ActiveLearning(torch.nn.Module):
    def __init__(self, exp_dict):
        super().__init__()
        self.backbone = models.vgg16(pretrained=exp_dict["imagenet_pretraining"], progress=True)
        num_ftrs = self.backbone.classifier[-1].in_features
        self.backbone.classifier[-1] = torch.nn.Linear(num_ftrs, exp_dict["num_classes"])
        self.backbone.cuda()

        self.batch_size = exp_dict['batch_size']
        self.learning_epoch = exp_dict['learning_epoch']
        self.optimizer = torch.optim.SGD(self.backbone.parameters(),
                                         lr=exp_dict['lr'],
                                         weight_decay=5e-4,
                                         momentum=0.9,
                                         nesterov=True)
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer,
                                                                    mode='min',
                                                                    factor=0.1,
                                                                    patience=10,
                                                                    verbose=True)
        self.criterion = CrossEntropyLoss()
        self.heuristic = get_heuristic(exp_dict['heuristic'])
        self.wrapper = ModelWrapper(self.backbone, criterion=self.criterion)
        self.wrapper.add_metric('cls_report', lambda: ClassificationReport(exp_dict["num_classes"]))
        self.loop = ActiveLearningLoop(None, self.wrapper.predict_on_dataset,
                                       heuristic=self.heuristic,
                                       ndata_to_label=exp_dict['query_size'],
                                       batch_size=self.batch_size,
                                       iterations=exp_dict['iterations'],
                                       use_cuda=True)
        self.active_dataset = None
        self.active_dataset_settings = None

    def train_on_loader(self, loader: DataLoader):
        if self.active_dataset is None:
            self.active_dataset = loader.dataset
            if self.active_dataset_settings is not None:
                self.active_dataset.load_state_dict(self.active_dataset_settings)
            self.loop.dataset = self.active_dataset

        self.wrapper.train_on_dataset(self.active_dataset, self.optimizer, self.batch_size,
                                      epoch=self.learning_epoch, use_cuda=True)

        metrics = self.wrapper.metrics
        return self._format_metrics(metrics, 'train')

    @torch.no_grad()
    def val_on_loader(self, loader, savedir=None):
        val_data = loader.dataset
        self.wrapper.test_on_dataset(val_data)
        metrics = self.wrapper.metrics
        self.scheduler.step(metrics['test_loss'].value)
        self.loop.step()
        return self._format_metrics(metrics, 'test')

    def _format_metrics(self, metrics, step):
        mets = {k: v.value for k, v in metrics if step in k}
        mets = {k: v if isinstance(v, float) else np.mean(v) for k, v in mets.items()}
        return mets

    def get_state_dict(self):
        state = {}
        state["model"] = self.backbone.state_dict()
        state["optimizer"] = self.optimizer.state_dict()
        state["scheduler"] = self.scheduler.state_dict()
        if self.active_dataset is None:
            state['dataset'] = None
        else:
            state["dataset"] = self.active_dataset.state_dict()
        return state

    def set_state_dict(self, state_dict):
        self.backbone.load_state_dict(state_dict["model"])
        self.optimizer.load_state_dict(state_dict["optimizer"])
        self.scheduler.load_state_dict(state_dict["scheduler"])
        self.active_dataset_settings = state_dict["dataset"]
