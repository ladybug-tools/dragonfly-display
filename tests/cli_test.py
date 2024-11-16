"""Test cli."""
import os
import time
from click.testing import CliRunner

from ladybug.commandutil import run_command_function
from dragonfly_display.cli import model_to_vis_set_cli, model_to_vis_set, \
    model_comparison_to_vis_set_cli, model_comparison_to_vis_set


def test_model_to_vis_set_cli():
    """Test the model-to-vis command as it runs in the CLI."""
    input_model = './tests/json/model_with_doors_skylights.dfjson'
    output_vis = './tests/json/model_with_doors_skylights.html'
    runner = CliRunner()
    t0 = time.time()
    cmd_args = [input_model, '--output-format', 'html', '--output-file', output_vis]
    result = runner.invoke(model_to_vis_set_cli, cmd_args)
    run_time = time.time() - t0
    assert result.exit_code == 0
    assert run_time < 10
    assert os.path.isfile(output_vis)
    os.remove(output_vis)


def test_model_to_vis_set():
    """Test the model_to_vis_set function that runs within the CLI."""
    input_model = './tests/json/model_with_doors_skylights.dfjson'
    cmd_args = [input_model]
    cmd_options = {'--output-format': 'vtkjs'}
    vtkjs_str = run_command_function(model_to_vis_set, cmd_args, cmd_options)

    assert isinstance(vtkjs_str, str)
    assert len(vtkjs_str) > 1000

    cmd_options = {
        '--color-by': 'type',
        '--output-format': 'html',
        '--room-attr': 'display_name',
        '--text-attr': ''
    }
    output_vis = './tests/json/model_with_doors_skylights.html'
    cmd_options['--output-file'] = output_vis
    run_command_function(model_to_vis_set, cmd_args, cmd_options)
    assert os.path.isfile(output_vis)
    os.remove(output_vis)


def test_model_comparison_to_vis_set_cli():
    """Test the model_comparison_to_vis_set function that runs within the CLI."""
    base_model = './tests/json/base_model.dfjson'
    incoming_model = './tests/json/incoming_model.dfjson'
    output_vis = './tests/json/comparison.html'
    runner = CliRunner()
    t0 = time.time()
    cmd_args = [base_model, incoming_model, '--output-format', 'html',
                '--output-file', output_vis]
    result = runner.invoke(model_comparison_to_vis_set_cli, cmd_args)
    run_time = time.time() - t0
    assert result.exit_code == 0
    assert run_time < 10
    assert os.path.isfile(output_vis)
    os.remove(output_vis)


def test_model_comparison_to_vis_set():
    """Test the model_comparison_to_vis_set function."""
    base_model = './tests/json/base_model.dfjson'
    incoming_model = './tests/json/incoming_model.dfjson'
    cmd_args = [base_model, incoming_model]
    cmd_options = {'--output-format': 'vtkjs'}
    vtkjs_str = run_command_function(model_comparison_to_vis_set, cmd_args, cmd_options)

    assert isinstance(vtkjs_str, str)
    assert len(vtkjs_str) > 1000

