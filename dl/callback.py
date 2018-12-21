from typing import Dict, Callable, List
from catalyst.utils.factory import UtilsFactory


class Callback:
    """
    An abstract class that all callback(e.g., Logger) classes extends from.
    Must be extended before usage.

    usage example:

    mode start (train/infer/debug)
        epoch start (one epoch - one run of every loader)
            loader start
                batch start
                batch handler
                batch end
            loader end
        epoch end
    mode end
    """

    def on_train_start(self, state):
        pass

    def on_train_end(self, state):
        pass

    def on_infer_start(self, state):
        pass

    def on_infer_end(self, state):
        pass

    def on_epoch_start(self, state):
        pass

    def on_epoch_end(self, state):
        pass

    def on_loader_start(self, state):
        pass

    def on_loader_end(self, state):
        pass

    def on_batch_start(self, state):
        pass

    def on_batch_end(self, state):
        pass


class CallbackCompose:
    def __init__(self, callbacks: Dict[str, Callback]):
        self.callbacks = callbacks

    def on_train_start(self, state):
        for key, value in self.callbacks.items():
            value.on_train_start(state=state)

    def on_train_end(self, state):
        for key, value in self.callbacks.items():
            value.on_train_end(state=state)

    def on_infer_start(self, state):
        for key, value in self.callbacks.items():
            value.on_infer_start(state=state)

    def on_infer_end(self, state):
        for key, value in self.callbacks.items():
            value.on_infer_end(state=state)

    def on_epoch_start(self, state):
        for key, value in self.callbacks.items():
            value.on_epoch_start(state=state)

    def on_epoch_end(self, state):
        for key, value in self.callbacks.items():
            value.on_epoch_end(state=state)

    def on_loader_start(self, state):
        for key, value in self.callbacks.items():
            value.on_loader_start(state=state)

    def on_loader_end(self, state):
        for key, value in self.callbacks.items():
            value.on_loader_end(state=state)

    def on_batch_start(self, state):
        for key, value in self.callbacks.items():
            value.on_batch_start(state=state)

    def on_batch_end(self, state):
        for key, value in self.callbacks.items():
            value.on_batch_end(state=state)


class MetricCallback(Callback):
    """
    A callback that returns single metric on `state.on_batch_end`
    """

    def __init__(
        self,
        prefix: str,
        metric_fn: Callable,
        input_key: str = "targets",
        output_key: str = "logits",
        **metric_params
    ):
        self.prefix = prefix
        self.metric_fn = metric_fn
        self.input_key = input_key
        self.output_key = output_key
        self.metric_params = metric_params

    def on_batch_end(self, state):
        outputs = state.output[self.output_key]
        targets = state.input[self.input_key]

        metric = self.metric_fn(targets, outputs, **self.metric_params)
        state.batch_metrics[self.prefix
                            ] = UtilsFactory.get_val_from_metric(metric)


class MultiMetricCallback(Callback):
    """
    A callback that returns multiple metric on `state.on_batch_end`
    """

    def __init__(
        self,
        prefix: str,
        metric_fn: Callable,
        list_args: List,
        input_key: str = "targets",
        output_key: str = "logits",
        **metric_params
    ):
        self.prefix = prefix
        self.metric_fn = metric_fn
        self.list_args = list_args
        self.input_key = input_key
        self.output_key = output_key
        self.metric_params = metric_params

    def on_batch_end(self, state):
        outputs = state.output[self.output_key]
        targets = state.input[self.input_key]

        metrics = self.metric_fn(
            targets, outputs, self.list_args, **self.metric_params
        )

        for arg, metric in zip(self.list_args, metrics):
            key = f"{self.prefix}_{arg}"
            state.batch_metrics[key] = UtilsFactory.get_val_from_metric(metric)
