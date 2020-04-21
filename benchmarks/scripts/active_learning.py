from haven import haven_utils as hu

# Define exp groups for parameter search
EXP_GROUPS = {
    'active_char_noise':
        hu.cartesian_exp_group({
            'lr': [0.001],
            'batch_size': [32],
            'model': "active_learning",
            'seed': [1337, 1338, 1339, 1340],
            'mu': 1e-3,
            'reg_factor': 1e-4,
            'backbone': "vgg16",
            'num_classes': 52,
            'query_size': [10, 50, 100],
            'learning_epoch': 10,
            'heuristic': ['bald', 'random', 'entropy'],
            'iterations': [1, 20, 40, 60],
            'max_epoch': 2000,
            'imagenet_pretraining': [True],
            'dataset': {
                'path': '/mnt/datasets/public/research/synbols/missing-symbol_n=100000_2020-Apr-10.h5py',
                'name': 'active_learning',
                'task': 'char',
                'initial_pool': 2000,
                'seed': 1337,
                'uncertainty_config': {'is_bold': {}}}}),
'active_char_shuffle':
        hu.cartesian_exp_group({
            'lr': [0.001],
            'batch_size': [32],
            'model': "active_learning",
            'seed': [1337, 1338, 1339, 1340],
            'mu': 1e-3,
            'reg_factor': 1e-4,
            'backbone': "vgg16",
            'num_classes': 52,
            'query_size': [100],
            'shuffle_prop': [0.0, 0.025, 0.5, 0.1],
            'learning_epoch': 10,
            'heuristic': ['bald', 'random', 'entropy'],
            'iterations': [20],
            'max_epoch': 2000,
            'imagenet_pretraining': [True],
            'dataset': {
                'path': '/mnt/datasets/public/research/synbols/missing-symbol_n=100000_2020-Apr-10.h5py',
                'name': 'active_learning',
                'task': 'char',
                'initial_pool': 2000,
                'seed': 1337,
                'uncertainty_config': {'is_bold': {}}}}),
    'active_char_calibrated':
        hu.cartesian_exp_group({
            'lr': [0.001],
            'batch_size': [32],
            'model': "active_learning",
            'calibrate': True,
            'seed': [1337, 1338, 1339, 1340],
            'mu': 1e-3,
            'reg_factor': 1e-4,
            'backbone': "vgg16",
            'num_classes': 52,
            'query_size': [10, 50, 100],
            'learning_epoch': 10,
            'heuristic': ['bald', 'random', 'entropy'],
            'iterations': [1, 20, 40, 60],
            'max_epoch': 2000,
            'imagenet_pretraining': [True],
            'dataset': {
                'path': '/mnt/datasets/public/research/synbols/missing-symbol_n=100000_2020-Apr-10.h5py',
                'name': 'active_learning',
                'task': 'char',
                'initial_pool': 2000,
                'seed': 1337,
                'uncertainty_config': {'is_bold': {}}}})
}
