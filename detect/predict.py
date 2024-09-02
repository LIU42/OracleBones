import onnxruntime as ort
import utils.process as process

from wrappers import BoneScript


class ScriptDetector:
    def __init__(self, configs):
        if configs['device'] == 'GPU':
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        else:
            providers = ['CPUExecutionProvider']

        self.configs = configs
        self.session = ort.InferenceSession(f'detect/weights/product/detect-{self.precision}.onnx', providers=providers)

    def __call__(self, image):
        inputs = process.convert_input(image, precision=self.precision)

        outputs = self.session.run([], inputs)
        outputs = self.reshape(outputs)

        results = process.non_max_suppression(outputs, self.conf_threshold, self.iou_threshold)

        return [BoneScript.from_box(box) for box in results]

    @property
    def precision(self):
        return self.configs['precision']

    @property
    def conf_threshold(self):
        return self.configs['conf-threshold']

    @property
    def iou_threshold(self):
        return self.configs['iou-threshold']

    @staticmethod
    def reshape(outputs):
        return outputs[0].squeeze().transpose()
