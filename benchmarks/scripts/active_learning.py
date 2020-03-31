from haven import haven_utils as hu

# Define exp groups for parameter search
EXP_GROUPS = {'active_font':
    hu.cartesian_exp_group({
        'lr': [0.001],
        'batch_size': [32],
        'model': "active_learning",
        'calibrate': True,
        'mu': 1e-3,
        'reg_factor': 1e-4,
        'backbone': "vgg16",
        'num_classes': 1002,
        'query_size': [100],
        'learning_epoch': 10,
        'heuristic': ['bald', 'random', 'entropy'],
        'iterations': [1, 20],
        'max_epoch': 2000,
        'imagenet_pretraining': [True],
        'dataset': {
            'path': '/mnt/datasets/public/research/synbols/old/latin_res=32x32_n=100000.npz',
            'name': 'active_learning',
            'task': 'font',
            'p': 0.0,
            'initial_pool': 2000,
            'seed': 1337,
            'uncertainty_config': {'is_bold': {}}}}),
    'active_font_noise':
        hu.cartesian_exp_group({
            'lr': [0.001],
            'batch_size': [32],
            'model': "active_learning",
            'calibrate': True,
            'mu': 1e-3,
            'reg_factor': 1e-4,
            'backbone': "vgg16",
            'num_classes': 1002,
            'query_size': [100],
            'learning_epoch': 10,
            'heuristic': ['bald', 'random', 'entropy'],
            'iterations': [1, 20],
            'max_epoch': 2000,
            'imagenet_pretraining': [True],
            'dataset': {
                'path': '/mnt/datasets/public/research/synbols/old/latin_res=32x32_n=100000.npz',
                'name': 'active_learning',
                'task': 'font',
                'p': 0.1,
                'initial_pool': 2000,
                'seed': 1337,
                'uncertainty_config': {'is_bold': {}}}}),
    'active_char_calib':
        hu.cartesian_exp_group({
            'lr': [0.001],
            'batch_size': [32],
            'model': "active_learning",
            'calibrate': True,
            'mu': 1e-3,
            'reg_factor': 1e-4,
            'mu': 1e-3,
            'backbone': "vgg16",
            'num_classes': 52,
            'query_size': [100],
            'learning_epoch': 10,
            'heuristic': ['bald', 'random', 'entropy'],
            'iterations': [1, 20],
            'max_epoch': 2000,
            'imagenet_pretraining': [True],
            'dataset': {
                'path': '/mnt/datasets/public/research/synbols/old/latin_res=32x32_n=100000.npz',
                'name': 'active_learning',
                'task': 'char',
                'p': 0.0,
                'initial_pool': 2000,
                'seed': 1337,
                'uncertainty_config': {'is_bold': {}}}}),
    'active_char_noise':
        hu.cartesian_exp_group({
            'lr': [0.001],
            'batch_size': [32],
            'model': "active_learning",
            'calibrate': True,
            'mu': 1e-3,
            'reg_factor': 1e-4,
            'backbone': "vgg16",
            'num_classes': 52,
            'query_size': [100],
            'learning_epoch': 10,
            'heuristic': ['bald', 'random', 'entropy'],
            'iterations': [1, 20],
            'max_epoch': 2000,
            'imagenet_pretraining': [True],
            'dataset': {
                'path': '/mnt/datasets/public/research/synbols/old/latin_res=32x32_n=100000.npz',
                'name': 'active_learning',
                'task': 'char',
                'p': 0.1,
                'initial_pool': 2000,
                'seed': 1337,
                'uncertainty_config': {'is_bold': {}}}}),
    'active_char_5_cls_noise':
        hu.cartesian_exp_group({
            'lr': [0.001],
            'batch_size': [32],
            'model': "active_learning",
            'calibrate': True,
            'mu': 1e-3,
            'reg_factor': 1e-4,
            'backbone': "vgg16",
            'num_classes': 52,
            'query_size': [100],
            'learning_epoch': 10,
            'heuristic': ['bald', 'random', 'entropy'],
            'iterations': [1, 20],
            'max_epoch': 2000,
            'imagenet_pretraining': [True],
            'dataset': {
                'path': '/mnt/datasets/public/research/synbols/old/latin_res=32x32_n=100000.npz',
                'name': 'active_learning',
                'task': 'char',
                'p': 0.1,
                'initial_pool': 2000,
                'n_classes': 5,
                'seed': 1337,
                'uncertainty_config': {'is_bold': {}}}}),

    'active_char_5_cls_25noise':
        hu.cartesian_exp_group({
            'lr': [0.001],
            'batch_size': [32],
            'model': "active_learning",
            'calibrate': True,
            'mu': 1e-3,
            'reg_factor': 1e-4,
            'backbone': "vgg16",
            'num_classes': 52,
            'query_size': [100],
            'learning_epoch': 10,
            'heuristic': ['bald', 'random', 'entropy'],
            'iterations': [1, 20],
            'max_epoch': 2000,
            'imagenet_pretraining': [True],
            'dataset': {
                'path': '/mnt/datasets/public/research/synbols/old/latin_res=32x32_n=100000.npz',
                'name': 'active_learning',
                'task': 'char',
                'p': 0.25,
                'initial_pool': 2000,
                'n_classes': 5,
                'seed': 1337,
                'uncertainty_config': {'is_bold': {}}}})
}
