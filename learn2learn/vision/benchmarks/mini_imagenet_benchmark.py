#!/usr/bin/env python3

import learn2learn as l2l

from learn2learn.data.transforms import NWays, KShots, LoadData, RemapLabels, ConsecutiveLabels
from torchvision.transforms import (Compose, ToPILImage, ToTensor, RandomCrop, RandomHorizontalFlip,
                                    ColorJitter, Normalize)


def mini_imagenet_tasksets(
    train_ways=5,
    train_samples=10,
    test_ways=5,
    test_samples=10,
    root='~/data',
    data_augmentation=None, #해당 부분이 없다.
    **kwargs,
):
    """Tasksets for mini-ImageNet benchmarks."""
    if data_augmentation is None:
        train_data_transforms = None
        test_data_transforms = None
    elif data_augmentation == 'normalize':
        train_data_transforms = Compose([
            lambda x: x / 255.0,
        ])
        test_data_transforms = train_data_transforms
    elif data_augmentation == 'lee2019':
        normalize = Normalize(
            mean=[120.39586422/255.0, 115.59361427/255.0, 104.54012653/255.0],
            std=[70.68188272/255.0, 68.27635443/255.0, 72.54505529/255.0],
        )
        train_data_transforms = Compose([
            ToPILImage(),
            RandomCrop(84, padding=8),
            ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4),
            RandomHorizontalFlip(),
            ToTensor(),
            normalize,
        ])
        test_data_transforms = Compose([
            normalize,
        ])
    else:
        raise('Invalid data_augmentation argument.')

    train_dataset = l2l.vision.datasets.MiniImagenet(
        root=root,
        mode='train',
        transform=train_data_transforms,
        download=True,
    )
    valid_dataset = l2l.vision.datasets.MiniImagenet(
        root=root,
        mode='validation',
        transform=test_data_transforms,
        download=True,
    )
    test_dataset = l2l.vision.datasets.MiniImagenet(
        root=root,
        mode='test',
        transform=test_data_transforms,
        download=True,
    )
    train_dataset = l2l.data.MetaDataset(train_dataset)
    train_classes = train_dataset.labels
    valid_dataset = l2l.data.MetaDataset(valid_dataset)
    test_dataset = l2l.data.MetaDataset(test_dataset)
    test_labels = test_dataset.labels
    test_labels = [t + len(train_dataset.labels) + len(valid_dataset.labels) for t in test_labels ]

    train_transforms = [
        NWays(train_dataset, train_ways),
        KShots(train_dataset, train_samples),
        LoadData(train_dataset),
        RemapLabels(train_dataset),
        ConsecutiveLabels(train_dataset),
    ]
    valid_transforms = [
        NWays(valid_dataset, test_ways),
        KShots(valid_dataset, test_samples),
        LoadData(valid_dataset),
        ConsecutiveLabels(valid_dataset),
        RemapLabels(valid_dataset),
    ]
    test_transforms = [
        NWays(test_dataset, test_ways),
        KShots(test_dataset, test_samples),
        LoadData(test_dataset),
        RemapLabels(test_dataset),
        ConsecutiveLabels(test_dataset),
    ]

    _datasets = (train_dataset, valid_dataset, test_dataset)
    _transforms = (train_transforms, valid_transforms, test_transforms)
    return _datasets, _transforms,train_classes,test_labels
