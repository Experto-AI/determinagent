import pytest
import yaml

from determinagent.config import load_config, load_config_from_string, merge_configs
from determinagent.exceptions import ConfigurationError


class TestLoadConfig:
    def test_load_config_explicit_path(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_data = {"key": "value"}
        config_file.write_text(yaml.dump(config_data))

        loaded = load_config(path=config_file)
        assert loaded == config_data

    def test_load_config_not_found_not_required(self):
        loaded = load_config(path="non_existent.yaml", required=False)
        assert loaded == {}

    def test_load_config_not_found_required(self):
        with pytest.raises(ConfigurationError, match="Required configuration file not found"):
            load_config(path="non_existent.yaml", required=True)

    def test_load_config_invalid_yaml(self, tmp_path):
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid: yaml: :")

        with pytest.raises(ConfigurationError, match="Invalid YAML in configuration file"):
            load_config(path=config_file)

    def test_load_config_empty_file(self, tmp_path):
        config_file = tmp_path / "empty.yaml"
        config_file.write_text("")

        loaded = load_config(path=config_file)
        assert loaded == {}

    def test_load_config_auto_discover(self, tmp_path, monkeypatch):
        # Mock sys.argv[0] to simulate a script named 'myscript.py'
        script_path = tmp_path / "myscript.py"
        script_path.touch()
        monkeypatch.setattr("sys.argv", [str(script_path)])

        config_path = tmp_path / "myscript.yaml"
        config_data = {"auto": "discovered"}
        config_path.write_text(yaml.dump(config_data))

        # When path is None, it should look for myscript.yaml
        loaded = load_config()
        assert loaded == config_data


class TestLoadConfigFromString:
    def test_load_config_from_string_success(self):
        content = "name: test\nvalue: 123"
        loaded = load_config_from_string(content)
        assert loaded == {"name": "test", "value": 123}

    def test_load_config_from_string_empty(self):
        assert load_config_from_string("") == {}

    def test_load_config_from_string_invalid(self):
        with pytest.raises(ConfigurationError, match="Invalid YAML content"):
            load_config_from_string("invalid: yaml: :")


class TestMergeConfigs:
    def test_merge_configs_basic(self):
        c1 = {"a": 1, "b": 2}
        c2 = {"b": 3, "c": 4}
        merged = merge_configs(c1, c2)
        assert merged == {"a": 1, "b": 3, "c": 4}

    def test_merge_configs_nested(self):
        c1 = {"agent": {"model": "fast", "provider": "claude"}}
        c2 = {"agent": {"model": "powerful"}}
        merged = merge_configs(c1, c2)
        assert merged == {"agent": {"model": "powerful", "provider": "claude"}}

    def test_merge_configs_multiple(self):
        c1 = {"a": 1}
        c2 = {"b": 2}
        c3 = {"a": 3}
        merged = merge_configs(c1, c2, c3)
        assert merged == {"a": 3, "b": 2}

    def test_merge_configs_non_dict_override(self):
        c1 = {"a": {"nested": 1}}
        c2 = {"a": 2}
        merged = merge_configs(c1, c2)
        assert merged == {"a": 2}
