import os
import torch
from torch.utils.data import DataLoader
from flood_forecast.time_model import PyTorchForecast
from flood_forecast.pytorch_training import torch_single_train
import unittest
from flood_forecast.pytorch_training import train_transformer_style


class PyTorchTrainTests(unittest.TestCase):
    def setUp(self):
        self.test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_init")
        self.model_params = {
            "model_params": {
                "number_time_series": 3,
                "seq_len": 20},
            "dataset_params": {
                "forecast_history": 20,
                "class": "default",
                "forecast_length": 20,
                "relevant_cols": [
                    "cfs",
                    "temp",
                    "precip"],
                "target_col": ["cfs"],
                "interpolate": False},
            "training_params": {
                "optimizer": "Adam",
                "lr": .1,
                "criterion": "MSE",
                "epochs": 1,
                "batch_size": 2,
                "optim_params": {}},
            "wandb": False,
            "inference_params": {
                "hours_to_forecast": 10}}
        self.keag_file = os.path.join(self.test_path, "keag_small.csv")
        self.model = PyTorchForecast(
            "MultiAttnHeadSimple",
            self.keag_file,
            self.keag_file,
            self.keag_file,
            self.model_params)
        self.dummy_model = PyTorchForecast(
            "DummyTorchModel", self.keag_file, self.keag_file, self.keag_file, {
                "model_params": {"forecast_length": 5},
                "dataset_params": {
                    "forecast_history": 5,
                    "class": "default",
                    "forecast_length": 5,
                    "relevant_cols": ["cfs", "temp", "precip"],
                    "target_col": ["cfs"], "interpolate": False,
                    "train_end": 100
                },
                "training_params": {
                    "optimizer": "Adam",
                    "lr": .1,
                    "criterion": "MSE",
                    "epochs": 1,
                    "batch_size": 2,
                    "optim_params": {}
                },
                "inference_params": {"hours_to_forecast": 15},
                "wandb": False}
        )
        self.full_transformer_params = {
            "use_decoder": True,
            "model_params": {
                "number_time_series": 3,
                "seq_length": 20,
                "output_seq_len": 15},
            "dataset_params": {
                "forecast_history": 20,
                "class": "default",
                "forecast_length": 15,
                "relevant_cols": [
                    "cfs",
                    "temp",
                    "precip"],
                "target_col": ["cfs"],
                "interpolate": False,
                "train_end": 50,
                "valid_end": 100},
            "training_params": {
                "optimizer": "Adam",
                "lr": .01,
                "criterion": "MSE",
                "epochs": 1,
                "batch_size": 2,
                "optim_params": {}},
            "inference_params": {
                "hours_to_forecast": 10},
            "wandb": False}
        self.simple_param = {
            "use_decoder": True,
            "model_params": {
                "n_time_series": 3,
                "seq_length": 80,
                "output_seq_len": 20},
            "dataset_params": {
                "forecast_history": 20,
                "class": "default",
                "forecast_length": 15,
                "relevant_cols": [
                    "cfs",
                    "temp",
                    "precip"],
                "target_col": ["cfs"],
                "interpolate": False,
                "train_end": 50,
                "valid_end": 100},
            "inference_params": {
                "hours_to_forecast": 10},
            "training_params": {
                "optimizer": "Adam",
                "lr": .01,
                "criterion": "MSE",
                "epochs": 1,
                "batch_size": 2,
                "optim_params": {}},
            "wandb": False}
        self.transformer = PyTorchForecast(
            "SimpleTransformer",
            self.keag_file,
            self.keag_file,
            self.keag_file,
            self.full_transformer_params)
        self.simple_linear_model = PyTorchForecast(
            "SimpleLinearModel",
            self.keag_file,
            self.keag_file,
            self.keag_file,
            self.simple_param)
        self.opt = torch.optim.Adam(self.dummy_model.model.parameters(), lr=0.0001)
        self.criterion = torch.nn.modules.loss.MSELoss()
        self.data_loader = DataLoader(
            self.dummy_model.training,
            batch_size=2,
            shuffle=False,
            sampler=None,
            batch_sampler=None,
            num_workers=0,
            collate_fn=None,
            pin_memory=False,
            drop_last=False,
            timeout=0,
            worker_init_fn=None)
        # TODO add LSTM test self.lstm =

    def test_pytorch_train_base(self):
        self.assertEqual(self.model.model.dense_shape.in_features, 3)
        self.assertEqual(self.model.model.multi_attn.embed_dim, 128)

    def test_train_and_resume(self):
        train_transformer_style(self.model, self.model_params["training_params"])
        self.assertEqual(len(os.listdir("model_save")), 2)
        print("first test passed")
        model2 = PyTorchForecast(
            "MultiAttnHeadSimple",
            self.keag_file,
            self.keag_file,
            self.keag_file,
            self.model_params)
        data = torch.rand(2, 20, 3)
        self.model_params["weight_path"] = os.path.join(
            "model_save", sorted(os.listdir("model_save"))[1])
        print("Moving to next test")
        model3 = PyTorchForecast(
            "MultiAttnHeadSimple",
            self.keag_file,
            self.keag_file,
            self.keag_file,
            self.model_params)
        print("model loaded")
        basic_model = model2.model
        basic_model.eval()
        print("more model stuff")
        pre_loaded_model = model3.model
        pre_loaded_model.eval()
        print("passed model stuff")
        self.assertFalse(torch.allclose(pre_loaded_model(data), basic_model(data)))
        print("first test good")
        self.assertTrue(torch.allclose(basic_model(data), basic_model(data)))

    def test_transfer_shit(self):
        self.model_params["weight_path"] = os.path.join(
            "model_save", sorted(os.listdir("model_save"))[1])
        self.model_params["model_params"]["output_seq_len"] = 6
        self.model_params["weight_path_add"] = {}
        model3 = PyTorchForecast(
            "MultiAttnHeadSimple",
            self.keag_file,
            self.keag_file,
            self.keag_file,
            self.model_params)
        # Assert shape is proper
        self.assertEqual(2, 2)
        data = torch.rand(1, 20, 3)
        self.assertEqual(model3.model(data).shape, torch.Size([1, 6]))

    def test_removing_layer_param(self):
        model3 = PyTorchForecast(
            "MultiAttnHeadSimple",
            self.keag_file,
            self.keag_file,
            self.keag_file,
            self.model_params)
        model3.save_model("output.pth", 2)
        self.model_params["model_params"]["output_seq_len"] = 7
        self.model_params["weight_path_add"] = {}
        self.model_params["weight_path_add"]["excluded_layers"] = [
            "last_layer.weight", "last_layer.bias"]
        model = PyTorchForecast(
            "MultiAttnHeadSimple",
            self.keag_file,
            self.keag_file,
            self.keag_file,
            self.model_params)
        result = model.model(torch.rand(1, 20, 3))
        self.assertEqual(result.shape[1], 7)

    def test_train_loss(self):
        print("Now begining train loss test")
        total_loss = torch_single_train(
            self.dummy_model,
            self.opt,
            self.criterion,
            self.data_loader,
            False)
        self.assertGreater(total_loss, 100)
        self.assertGreater(total_loss, 752, 000)
        self.assertLess(total_loss, 802000)

    # def test_train_full_transformer(self):
    #     print("Now begining transformer tests")
    #     train_transformer_style(self.transformer, self.full_transformer_params["training_params"], True)
    #     self.assertEqual(1, 1)
    #
    # def test_transfom_validation(self):
    #     # TODO add
    #     pass

    def linear_model_test(self):
        train_transformer_style(
            self.simple_linear_model,
            self.simple_param["training_params"],
            True)


if __name__ == '__main__':
    unittest.main()
