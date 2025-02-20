# Authors: Alexandre Gramfort
#          Lukas Gemein <l.gemein@gmail.com>
#          Hubert Banville <hubert.jbanville@gmail.com>
#          Robin Schirrmeister <robintibor@gmail.com>
#          Daniel Wilson <dan.c.wil@gmail.com>
#
# License: BSD-3


from collections import OrderedDict

import numpy as np
import torch
import pytest

from braindecode.models import (
    Deep4Net,
    EEGNetv4,
    EEGNetv1,
    HybridNet,
    ShallowFBCSPNet,
    EEGResNet,
    TCN,
    SleepStagerChambon2018,
    SleepStagerBlanco2020,
    SleepStagerEldele2021,
    USleep,
    DeepSleepNet,
    EEGITNet,
    EEGInception,
    EEGInceptionERP,
    EEGInceptionMI,
    TIDNet,
    ATCNet,
    EEGConformer,
)

from braindecode.util import set_random_seeds


@pytest.fixture(scope="module")
def input_sizes():
    return dict(n_channels=18, n_in_times=600, n_classes=2, n_samples=7)


def check_forward_pass(model, input_sizes, only_check_until_dim=None):
    # Test 4d Input
    set_random_seeds(0, False)
    rng = np.random.RandomState(42)
    X = rng.randn(
        input_sizes["n_samples"],
        input_sizes["n_channels"],
        input_sizes["n_in_times"],
        1,
    )
    X = torch.Tensor(X.astype(np.float32))
    y_pred = model(X)
    assert y_pred.shape[:only_check_until_dim] == (
        input_sizes["n_samples"],
        input_sizes["n_classes"],
    )

    # Test 3d input
    set_random_seeds(0, False)
    X = X.squeeze(-1)
    assert len(X.shape) == 3
    y_pred_new = model(X)
    assert y_pred_new.shape[:only_check_until_dim] == (
        input_sizes["n_samples"],
        input_sizes["n_classes"],
    )
    np.testing.assert_allclose(
        y_pred.detach().cpu().numpy(),
        y_pred_new.detach().cpu().numpy(),
        atol=1e-4,
        rtol=0,
    )


def test_shallow_fbcsp_net(input_sizes):
    model = ShallowFBCSPNet(
        input_sizes["n_channels"],
        input_sizes["n_classes"],
        input_sizes["n_in_times"],
        final_conv_length="auto",
    )
    check_forward_pass(model, input_sizes)


def test_shallow_fbcsp_net_load_state_dict(input_sizes):
    model = ShallowFBCSPNet(
        input_sizes["n_channels"],
        input_sizes["n_classes"],
        input_sizes["n_in_times"],
        final_conv_length="auto",
    )

    state_dict = OrderedDict()
    state_dict["conv_time.weight"] = torch.rand([40, 1, 25, 1])
    state_dict["conv_time.bias"] = torch.rand([40])
    state_dict["conv_spat.weight"] = torch.rand([40, 40, 1, input_sizes["n_channels"]])
    state_dict["bnorm.weight"] = torch.rand([40])
    state_dict["bnorm.bias"] = torch.rand([40])
    state_dict["bnorm.running_mean"] = torch.rand([40])
    state_dict["bnorm.running_var"] = torch.rand([40])
    state_dict["bnorm.num_batches_tracked"] = torch.rand([])
    state_dict["conv_classifier.weight"] = torch.rand(
        [input_sizes["n_classes"], 40, model.final_conv_length, 1]
    )
    state_dict["conv_classifier.bias"] = torch.rand([input_sizes["n_classes"]])
    model.load_state_dict(state_dict)


def test_deep4net(input_sizes):
    model = Deep4Net(
        input_sizes["n_channels"],
        input_sizes["n_classes"],
        input_sizes["n_in_times"],
        final_conv_length="auto",
    )
    check_forward_pass(model, input_sizes)


def test_deep4net_load_state_dict(input_sizes):
    model = Deep4Net(
        input_sizes["n_channels"],
        input_sizes["n_classes"],
        input_sizes["n_in_times"],
        final_conv_length="auto",
    )
    state_dict = OrderedDict()
    state_dict["conv_time.weight"] = torch.rand([25, 1, 10, 1])
    state_dict["conv_time.bias"] = torch.rand([25])
    state_dict["conv_spat.weight"] = torch.rand([25, 25, 1, input_sizes["n_channels"]])
    state_dict["bnorm.weight"] = torch.rand([25])
    state_dict["bnorm.bias"] = torch.rand([25])
    state_dict["bnorm.running_mean"] = torch.rand([25])
    state_dict["bnorm.running_var"] = torch.rand([25])
    state_dict["bnorm.num_batches_tracked"] = torch.rand([])
    state_dict["conv_2.weight"] = torch.rand([50, 25, 10, 1])
    state_dict["bnorm_2.weight"] = torch.rand([50])
    state_dict["bnorm_2.bias"] = torch.rand([50])
    state_dict["bnorm_2.running_mean"] = torch.rand([50])
    state_dict["bnorm_2.running_var"] = torch.rand([50])
    state_dict["bnorm_2.num_batches_tracked"] = torch.rand([])
    state_dict["conv_3.weight"] = torch.rand([100, 50, 10, 1])
    state_dict["bnorm_3.weight"] = torch.rand([100])
    state_dict["bnorm_3.bias"] = torch.rand([100])
    state_dict["bnorm_3.running_mean"] = torch.rand([100])
    state_dict["bnorm_3.running_var"] = torch.rand([100])
    state_dict["bnorm_3.num_batches_tracked"] = torch.rand([])
    state_dict["conv_4.weight"] = torch.rand([200, 100, 10, 1])
    state_dict["bnorm_4.weight"] = torch.rand([200])
    state_dict["bnorm_4.bias"] = torch.rand([200])
    state_dict["bnorm_4.running_mean"] = torch.rand([200])
    state_dict["bnorm_4.running_var"] = torch.rand([200])
    state_dict["bnorm_4.num_batches_tracked"] = torch.rand([])
    state_dict["conv_classifier.weight"] = torch.rand(
        [input_sizes["n_classes"], 200, model.final_conv_length, 1]
    )
    state_dict["conv_classifier.bias"] = torch.rand([input_sizes["n_classes"]])
    model.load_state_dict(state_dict)


def test_eegresnet(input_sizes):
    model = EEGResNet(
        input_sizes["n_channels"],
        input_sizes["n_classes"],
        input_sizes["n_in_times"],
        final_pool_length=5,
        n_first_filters=2,
    )
    check_forward_pass(model, input_sizes, only_check_until_dim=2)


def test_eegresnet_pool_length_auto(input_sizes):
    model = EEGResNet(
        input_sizes["n_channels"],
        input_sizes["n_classes"],
        input_sizes["n_in_times"],
        final_pool_length="auto",
        n_first_filters=2,
    )
    check_forward_pass(model, input_sizes, only_check_until_dim=2)


def test_hybridnet(input_sizes):
    model = HybridNet(
        input_sizes["n_channels"],
        input_sizes["n_classes"],
        input_sizes["n_in_times"],
    )
    check_forward_pass(model, input_sizes, only_check_until_dim=2)


def test_eegnet_v4(input_sizes):
    model = EEGNetv4(
        input_sizes["n_channels"],
        input_sizes["n_classes"],
        input_window_samples=input_sizes["n_in_times"],
    )
    check_forward_pass(model, input_sizes)


def test_eegnet_v1(input_sizes):
    model = EEGNetv1(
        input_sizes["n_channels"],
        input_sizes["n_classes"],
        input_window_samples=input_sizes["n_in_times"],
    )
    check_forward_pass(
        model,
        input_sizes,
    )


def test_tcn(input_sizes):
    model = TCN(
        input_sizes["n_channels"],
        input_sizes["n_classes"],
        n_filters=5,
        n_blocks=2,
        kernel_size=4,
        drop_prob=0.5,
        add_log_softmax=True,
    )
    check_forward_pass(model, input_sizes, only_check_until_dim=2)


def test_eegitnet(input_sizes):
    model = EEGITNet(
        n_outputs=input_sizes['n_classes'],
        n_chans=input_sizes['n_channels'],
        n_times=input_sizes['n_in_times'],
      )

    check_forward_pass(
        model,
        input_sizes,
    )


@pytest.mark.parametrize("model_cls", [EEGInception, EEGInceptionERP])
def test_eeginception_erp(input_sizes, model_cls):
    model = model_cls(
        n_outputs=input_sizes['n_classes'],
        n_chans=input_sizes['n_channels'],
        n_times=input_sizes['n_in_times'],
    )

    check_forward_pass(
        model,
        input_sizes,
    )


@pytest.mark.parametrize("model_cls", [EEGInception, EEGInceptionERP])
def test_eeginception_erp_n_params(model_cls):
    """Make sure the number of parameters is the same as in the paper when
    using the same architecture hyperparameters.
    """
    model = model_cls(
        n_chans=8,
        n_outputs=2,
        n_times=128,  # input_time
        sfreq=128,
        drop_prob=0.5,
        n_filters=8,
        scales_samples_s=(0.5, 0.25, 0.125),
        activation=torch.nn.ELU(),
    )

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    assert n_params == 14926  # From paper's TABLE IV EEG-Inception Architecture Details


def test_eeginception_mi(input_sizes):
    sfreq = 250
    model = EEGInceptionMI(
        n_outputs=input_sizes['n_classes'],
        n_chans=input_sizes['n_channels'],
        input_window_seconds=input_sizes['n_in_times'] / sfreq,
        sfreq=sfreq,
    )

    check_forward_pass(model, input_sizes, )


@pytest.mark.parametrize(
    "n_filter,reported",
    [(6, 51386), (12, 204002), (16, 361986), (24, 812930), (64, 5767170)],
)
def test_eeginception_mi_binary_n_params(n_filter, reported):
    """Make sure the number of parameters is the same as in the paper when
    using the same architecture hyperparameters.

    Note
    ----
    For some reason, we match the correct number of parameters for all
    configurations in the binary classification case, but none for the 4-class
    case... Should be investigated by contacting the authors.
    """
    model = EEGInceptionMI(
        n_chans=3,
        n_outputs=2,
        input_window_seconds=3.,  # input_time
        sfreq=250,
        n_convs=3,
        n_filters=n_filter,
        kernel_unit_s=0.1,
    )

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    # From first column of TABLE 2 in EEG-Inception paper
    assert n_params == reported


def test_atcnet(input_sizes):
    sfreq = 250
    input_sizes["n_in_times"] = 1125
    model = ATCNet(
        n_chans=input_sizes['n_channels'],
        n_outputs=input_sizes['n_classes'],
        input_window_seconds=input_sizes['n_in_times'] / sfreq,
        sfreq=sfreq,
    )

    check_forward_pass(model, input_sizes, )


def test_atcnet_n_params():
    """Make sure the number of parameters is the same as in the paper when
    using the same architecture hyperparameters.
    """
    n_windows = 5
    att_head_dim = 8
    att_num_heads = 2

    model = ATCNet(
        n_chans=22,
        n_outputs=4,
        input_window_seconds=4.5,
        sfreq=250,
        n_windows=n_windows,
        att_head_dim=att_head_dim,
        att_num_heads=att_num_heads,
    )

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    # The paper states the models has around "115.2 K" parameters in its
    # conclusion. By analyzing the official tensorflow code, we found indeed
    # 115,172 parameters, but these take into account untrainable batch norm
    # params, while the number of trainable parameters is 113,732.
    official_code_nparams = 113_732

    assert n_params == official_code_nparams


@pytest.mark.parametrize(
    "n_channels,sfreq,n_classes,input_size_s",
    [(20, 128, 5, 30), (10, 256, 4, 20), (1, 64, 2, 30)],
)
def test_sleep_stager(n_channels, sfreq, n_classes, input_size_s):
    rng = np.random.RandomState(42)
    time_conv_size_s = 0.5
    max_pool_size_s = 0.125
    pad_size_s = 0.25
    n_examples = 10

    model = SleepStagerChambon2018(
        n_channels,
        sfreq,
        n_conv_chs=8,
        time_conv_size_s=time_conv_size_s,
        max_pool_size_s=max_pool_size_s,
        pad_size_s=pad_size_s,
        input_window_seconds=input_size_s,
        n_outputs=n_classes,
        dropout=0.25,
    )
    model.eval()

    X = rng.randn(n_examples, n_channels, int(sfreq * input_size_s))
    X = torch.from_numpy(X.astype(np.float32))

    y_pred1 = model(X)  # 3D inputs
    y_pred2 = model(X.unsqueeze(1))  # 4D inputs
    assert y_pred1.shape == (n_examples, n_classes)
    assert y_pred2.shape == (n_examples, n_classes)
    np.testing.assert_allclose(
        y_pred1.detach().cpu().numpy(), y_pred2.detach().cpu().numpy()
    )


@pytest.mark.parametrize(
    "in_chans,sfreq,n_classes,input_size_s",
    [(20, 128, 5, 30), (10, 100, 4, 20), (1, 64, 2, 30)],
)
def test_usleep(in_chans, sfreq, n_classes, input_size_s):
    rng = np.random.RandomState(42)
    n_examples = 10
    seq_length = 3

    model = USleep(
        n_chans=in_chans,
        sfreq=sfreq,
        n_outputs=n_classes,
        input_window_seconds=input_size_s,
        ensure_odd_conv_size=True,
    )
    model.eval()

    X = rng.randn(n_examples, in_chans, int(sfreq * input_size_s))
    X = torch.from_numpy(X.astype(np.float32))

    y_pred1 = model(X)  # 3D inputs : (batch, channels, time)
    y_pred2 = model(X.unsqueeze(1))  # 4D inputs : (batch, 1, channels, time)
    y_pred3 = model(
        torch.stack([X for idx in range(seq_length)], axis=1)
    )  # (batch, sequence, channels, time)
    assert y_pred1.shape == (n_examples, n_classes)
    assert y_pred2.shape == (n_examples, n_classes)
    assert y_pred3.shape == (n_examples, n_classes, seq_length)
    np.testing.assert_allclose(
        y_pred1.detach().cpu().numpy(), y_pred2.detach().cpu().numpy()
    )


def test_usleep_n_params():
    """Make sure the number of parameters is the same as in the paper when
    using the same architecture hyperparameters.
    """
    model = USleep(
        n_chans=2, sfreq=128, depth=12, n_time_filters=5,
        complexity_factor=1.67, with_skip_connection=True, n_outputs=5,
        input_window_seconds=30, time_conv_size_s=9 / 128)

    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    assert n_params == 3114337  # From paper's supplementary materials, Table 2


def test_sleep_stager_return_feats():
    n_channels = 2
    sfreq = 10
    input_size_s = 30
    n_classes = 3

    model = SleepStagerChambon2018(
        n_channels, sfreq, n_conv_chs=8, input_window_seconds=input_size_s,
        n_outputs=n_classes, return_feats=True)
    model.eval()

    rng = np.random.RandomState(42)
    X = rng.randn(10, n_channels, int(sfreq * input_size_s))
    X = torch.from_numpy(X.astype(np.float32))

    out = model(X)
    assert out.shape == (10, model.len_last_layer)


def test_tidnet(input_sizes):
    model = TIDNet(
        input_sizes["n_channels"],
        input_sizes["n_classes"],
        input_sizes["n_in_times"],
    )
    check_forward_pass(model, input_sizes)


@pytest.mark.parametrize(
    "sfreq,n_classes,input_size_s,d_model", [(100, 5, 30, 80), (125, 4, 30, 100)]
)
def test_eldele_2021(sfreq, n_classes, input_size_s, d_model):
    # (100, 5, 30, 80) - Physionet Sleep
    # (125, 4, 30, 100) - SHHS
    rng = np.random.RandomState(42)
    n_channels = 1
    n_examples = 10

    model = SleepStagerEldele2021(
      sfreq=sfreq, n_outputs=n_classes,
      input_window_seconds=input_size_s,
      d_model=d_model, return_feats=False,
    )
    model.eval()

    X = rng.randn(n_examples, n_channels, np.ceil(input_size_s * sfreq).astype(int))
    X = torch.from_numpy(X.astype(np.float32))

    y_pred1 = model(X)  # 3D inputs
    assert y_pred1.shape == (n_examples, n_classes)


def test_eldele_2021_feats():
    n_channels = 1
    sfreq = 100
    input_size_s = 30
    n_classes = 3
    n_examples = 10

    model = SleepStagerEldele2021(
      sfreq, input_window_seconds=input_size_s, n_outputs=n_classes,
      return_feats=True,
    )
    model.eval()

    rng = np.random.RandomState(42)
    X = rng.randn(n_examples, n_channels, int(sfreq * input_size_s))
    X = torch.from_numpy(X.astype(np.float32))

    out = model(X)
    assert out.shape == (n_examples, model.len_last_layer)


@pytest.mark.parametrize(
    "n_channels,sfreq,n_groups,n_classes,input_size_s",
    [(20, 128, 2, 5, 30), (10, 100, 2, 4, 20), (1, 64, 1, 2, 30)],
)
def test_blanco_2020(n_channels, sfreq, n_groups, n_classes, input_size_s):
    rng = np.random.RandomState(42)
    n_examples = 10

    model = SleepStagerBlanco2020(
      n_chans=n_channels, sfreq=sfreq, n_groups=n_groups,
      input_window_seconds=input_size_s, n_outputs=n_classes,
      return_feats=False,
    )
    model.eval()

    X = rng.randn(n_examples, n_channels, np.ceil(input_size_s * sfreq).astype(int))
    X = torch.from_numpy(X.astype(np.float32))

    y_pred1 = model(X)  # 3D inputs
    y_pred2 = model(X.unsqueeze(2))  # 4D inputs
    assert y_pred1.shape == (n_examples, n_classes)
    assert y_pred2.shape == (n_examples, n_classes)
    np.testing.assert_allclose(
        y_pred1.detach().cpu().numpy(), y_pred2.detach().cpu().numpy()
    )


def test_blanco_2020_feats():
    n_channels = 2
    sfreq = 50
    input_size_s = 30
    n_classes = 3
    n_examples = 10

    model = SleepStagerBlanco2020(
      n_channels, sfreq, input_window_seconds=input_size_s,
      n_outputs=n_classes, return_feats=True,
    )
    model.eval()

    rng = np.random.RandomState(42)
    X = rng.randn(n_examples, n_channels, int(sfreq * input_size_s))
    X = torch.from_numpy(X.astype(np.float32))

    out = model(X)
    assert out.shape == (n_examples, model.len_last_layer)


def test_eegitnet_shape():
    n_channels = 2
    sfreq = 50
    input_size_s = 30
    n_classes = 3
    n_examples = 10
    model = EEGITNet(
        n_classes=n_classes,
        in_channels=n_channels,
        input_window_samples=int(sfreq * input_size_s),
    )
    model.eval()

    rng = np.random.RandomState(42)
    X = rng.randn(n_examples, n_channels, int(sfreq * input_size_s))
    X = torch.from_numpy(X.astype(np.float32))

    out = model(X)
    assert out.shape == (n_examples, n_classes)


@pytest.mark.parametrize("n_classes", [5, 4, 2])
def test_deepsleepnet(n_classes):
    n_channels = 1
    sfreq = 100
    input_size_s = 30
    n_examples = 10

    model = DeepSleepNet(n_outputs=n_classes, return_feats=False)
    model.eval()

    rng = np.random.RandomState(42)
    X = rng.randn(n_examples, n_channels, np.ceil(input_size_s * sfreq).astype(int))
    X = torch.from_numpy(X.astype(np.float32))

    y_pred1 = model(X)  # 3D inputs
    y_pred2 = model(X.unsqueeze(1))  # 4D inputs
    assert y_pred1.shape == (n_examples, n_classes)
    assert y_pred2.shape == (n_examples, n_classes)
    np.testing.assert_allclose(
        y_pred1.detach().cpu().numpy(), y_pred2.detach().cpu().numpy()
    )


def test_deepsleepnet_feats():
    n_channels = 1
    sfreq = 100
    input_size_s = 30
    n_classes = 3
    n_examples = 10

    model = DeepSleepNet(n_outputs=n_classes, return_feats=True)
    model.eval()

    rng = np.random.RandomState(42)
    X = rng.randn(n_examples, n_channels, int(sfreq * input_size_s))
    X = torch.from_numpy(X.astype(np.float32))

    out = model(X.unsqueeze(1))
    assert out.shape == (n_examples, model.len_last_layer)


def test_deepsleepnet_feats_with_hook():
    n_channels = 1
    sfreq = 100
    input_size_s = 30
    n_classes = 3
    n_examples = 10

    model = DeepSleepNet(n_outputs=n_classes, return_feats=False)
    model.eval()

    rng = np.random.RandomState(42)
    X = rng.randn(n_examples, n_channels, int(sfreq * input_size_s))
    X = torch.from_numpy(X.astype(np.float32))

    def get_intermediate_layers(intermediate_layers, layer_name):
        def hook(model, input, output):
            intermediate_layers[layer_name] = output.flatten(start_dim=1).detach()

        return hook

    intermediate_layers = {}
    layer_name = "features_extractor"
    model.features_extractor.register_forward_hook(
        get_intermediate_layers(intermediate_layers, layer_name)
    )

    y_pred = model(X.unsqueeze(1))
    assert intermediate_layers["features_extractor"].shape == (
        n_examples,
        model.len_last_layer,
    )
    assert y_pred.shape == (n_examples, n_classes)


@pytest.fixture
def sample_input():
    batch_size = 16
    n_channels = 12
    n_timesteps = 1000
    return torch.rand(batch_size, n_channels, n_timesteps)


@pytest.fixture
def model():
    return EEGConformer(n_classes=2, n_channels=12)


def test_model_creation(model):
    assert model is not None


def test_conformer_forward_pass(sample_input, model):
    output = model(sample_input)
    assert isinstance(output, torch.Tensor)

    model_with_feature = EEGConformer(n_classes=2, n_channels=12, return_features=True)
    output = model_with_feature(sample_input)

    assert isinstance(output, tuple) and len(output) == 2


def test_patch_embedding(sample_input, model):
    patch_embedding = model.patch_embedding
    x = torch.unsqueeze(sample_input, dim=1)
    output = patch_embedding(x)
    assert output.shape[0] == sample_input.shape[0]


def test_model_trainable_parameters(model):
    patch_parameters = model.patch_embedding.parameters()
    transformer_parameters = model.transformer.parameters()
    classification_parameters = model.classification_head.parameters()

    trainable_patch_params = sum(p.numel() for p in patch_parameters if p.requires_grad)

    trainable_transformer_params = sum(
        p.numel() for p in transformer_parameters if p.requires_grad
    )

    trainable_classification_params = sum(
        p.numel() for p in classification_parameters if p.requires_grad
    )

    assert trainable_patch_params == 22000
    assert trainable_transformer_params == 118320
    assert trainable_classification_params == 633186
