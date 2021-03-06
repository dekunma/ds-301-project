import os
from PIL import Image
from bs4 import BeautifulSoup
import torch
from torchvision import transforms


class MaskDataset(object):
    def __init__(self, split, dataroot, test_size=0.2):
        self.transforms = transforms.Compose([
            transforms.ToTensor(), 
        ])
        # load all image files, sorting them to
        # ensure that they are aligned
        self.split = split
        self.dataroot = dataroot
        img_names = list(sorted(os.listdir(f"{dataroot}/images")))
        self.test_start_idx = int(len(img_names) * (1 - test_size))
        if split == 'train':
            self.imgs = img_names[:self.test_start_idx]
        elif split == 'test':
            self.imgs = img_names[self.test_start_idx:]
        else:
            raise NotImplementedError(f'split {split} not implemented.')

    def __getitem__(self, idx):
        idx += 0 if self.split == 'train' else self.test_start_idx # test set idx start from 683
        # load images ad masks
        file_image = 'maksssksksss'+ str(idx) + '.png'
        file_label = 'maksssksksss'+ str(idx) + '.xml'
        img_path = os.path.join(f"{self.dataroot}/images/", file_image)
        label_path = os.path.join(f"{self.dataroot}/annotations/", file_label)
        img = Image.open(img_path).convert("RGB")
        #Generate Label
        target = generate_target(idx, label_path)
        
        if self.transforms is not None:
            img = self.transforms(img)

        return img, target

    def __len__(self):
        return len(self.imgs)


def generate_target(image_id, file): 
    with open(file) as f:
        data = f.read()
        soup = BeautifulSoup(data, 'xml')
        objects = soup.find_all('object')

        # Bounding boxes for objects
        # In coco format, bbox = [xmin, ymin, width, height]
        # In pytorch, the input should be [xmin, ymin, xmax, ymax]
        boxes = []
        labels = []
        for i in objects:
            boxes.append(generate_box(i))
            labels.append(generate_label(i))
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        labels = torch.as_tensor(labels, dtype=torch.int64)
        # Tensorise img_id
        img_id = torch.tensor([image_id])
        # Annotation is in dictionary format
        target = {}
        target["boxes"] = boxes
        target["labels"] = labels
        target["image_id"] = img_id
        
        return target

def generate_box(obj):
    
    xmin = int(obj.find('xmin').text)
    ymin = int(obj.find('ymin').text)
    xmax = int(obj.find('xmax').text)
    ymax = int(obj.find('ymax').text)
    
    return [xmin, ymin, xmax, ymax]

def generate_label(obj):
    if obj.find('name').text == "without_mask":
        return 1
    elif obj.find('name').text == "with_mask":
        return 2
    elif obj.find('name').text == "mask_weared_incorrect":
        return 3
    
    else:
        raise Exception(f'Invalid label: {obj.find("name").text}')

def collate_fn(batch):
    return tuple(zip(*batch))