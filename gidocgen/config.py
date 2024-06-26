# SPDX-FileCopyrightText: 2021 GNOME Foundation <https://gnome.org>
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

import os
import re

toml_module = None
try:
    import tomllib as toml_lib
    toml_module = 'tomlib'
except ImportError:
    try:
        import tomli as toml_lib
        toml_module = 'tomli'
    except ImportError:
        import toml as toml_lib
        toml_module = 'toml'

from urllib.parse import urljoin
from packaging import version as packaging_version

from . import core, log, utils


class TomlConfig:
    """Wrapper class for TOML loading"""

    @staticmethod
    def load(toml):
        log.debug(f"Using TOML module: {toml_module}")
        if toml_module is None:
            log.error("No toml module found")
        elif toml_module in ['tomlib', 'tomli']:
            try:
                with open(toml, "rb") as f:
                    return toml_lib.load(f)
            except toml_lib.TOMLDecodeError as err:
                log.error(f"Invalid configuration file: {toml}: {err}")
        elif toml_module in ['toml']:
            try:
                return toml_lib.load(toml)
            except toml_lib.TomlDecodeError as err:
                log.error(f"Invalid configuration file: {toml}: {err}")


class GIDocConfig:
    """Load and represent the configuration for gidocgen"""
    def __init__(self, config_file=None):
        self._favicons = []
        self._config_file = config_file

        self._config = {}
        if self._config_file is not None:
            log.debug(f"Reading configuration file: {self._config_file}")
            self._config = TomlConfig.load(self._config_file)

    @property
    def library(self):
        return self._config.get('library', {})

    @property
    def extra(self):
        return self._config.get('extra', {})

    @property
    def theme(self):
        return self._config.get('theme', {})

    @property
    def check(self):
        return self._config.get('check', {})

    def get_templates_dir(self, default=None):
        return self.theme.get('templates_dir', default)

    def get_theme_name(self, default=None):
        return self.theme.get('name', default)

    def get_library_name(self, default=None):
        return self.library.get('name', default)

    def get_website_url(self, default=None):
        return self.library.get('website_url', default)

    def get_logo_url(self, default=None):
        return self.library.get('logo_url', default)

    def get_description(self, default=None):
        return self.library.get('description', default)

    @property
    def urlmap_file(self):
        return self.extra.get('urlmap_file')

    @property
    def urlmap_basename(self):
        if self.urlmap_file is not None:
            return os.path.basename(self.urlmap_file)
        return None

    @property
    def version(self):
        return self.library.get('version', 'Unknown')

    @property
    def authors(self):
        return self.library.get('authors', 'Unknown authors')

    @property
    def license(self):
        return self.library.get('license', 'All rights reserved')

    @property
    def website_url(self):
        return self.library.get('website_url', '')

    @property
    def docs_url(self):
        return self.library.get('docs_url', '')

    @property
    def browse_url(self):
        return self.library.get('browse_url', '')

    @property
    def logo_url(self):
        return self.library.get('logo_url', '')

    @property
    def description(self):
        return self.library.get('description', '')

    @property
    def dependencies(self):
        library = self._config.get('library', None)
        if library is None:
            return {}

        retval = {}
        dependencies = self._config.get('dependencies', {})
        for gir_name, dep in dependencies.items():
            res = {}
            res['name'] = dep.get('name', 'Unknown')
            res['description'] = dep.get('description', 'No description provided')
            res['docs_url'] = dep.get('docs_url', '#')
            retval[gir_name] = res
            log.debug(f"Found dependency {gir_name}: {res}")

        return retval

    @property
    def related(self):
        library = self._config.get('library', None)
        if library is None:
            return {}

        retval = {}
        dependencies = self._config.get('related', {})
        for gir_name, dep in dependencies.items():
            res = {}
            res['name'] = dep.get('name', 'Unknown')
            res['description'] = dep.get('description', 'No description provided')
            res['docs_url'] = dep.get('docs_url', '#')
            retval[gir_name] = res
            log.debug(f"Found related library {gir_name}: {res}")

        return retval

    @property
    def devhelp(self):
        return self.library.get('devhelp', False)

    @property
    def search_index(self):
        return self.library.get('search_index', False)

    @property
    def content_files(self):
        return self.extra.get('content_files', [])

    @property
    def content_images(self):
        return self.extra.get('content_images', [])

    @property
    def source_location_url(self):
        source_location = self._config.get('source-location', {})
        return source_location.get('base_url', '')

    @property
    def content_base_url(self):
        return self.extra.get('content_base_url')

    @property
    def file_format(self):
        source_location = self._config.get('source-location', {})
        return source_location.get('file_format', '{filename}#L{line}')

    @property
    def theme_name(self):
        return self.theme.get('name', '')

    @property
    def show_index_summary(self):
        return self.theme.get('show_index_summary', False)

    @property
    def show_class_hierarchy(self):
        if utils.find_program('dot') is None:
            return False
        return self.theme.get('show_class_hierarchy', False)

    def source_link(self, *args):
        (filename, line) = args[0]
        base_url = self.source_location_url
        file_format = self.file_format
        endpoint = file_format.replace('{filename}', filename)
        endpoint = endpoint.replace('{line}', str(line))
        return urljoin(base_url, endpoint)

    def content_link(self, content_file):
        base_url = self.content_base_url
        return urljoin(base_url, content_file)

    @property
    def objects(self):
        return self._config.get('object', {})

    def match_object(self, name, match_key, category=None, key=None):
        def obj_matches(obj, name):
            n = obj.get('name')
            p = obj.get('pattern')
            if n is not None and n == name:
                return True
            elif p is not None and re.match(p, name):
                return True
            return False
        for obj in self.objects:
            if obj_matches(obj, name):
                if category is None:
                    return obj.get(match_key, False)
                else:
                    assert key is not None
                obj_category = obj.get(category)
                if obj_category is None:
                    return False
                for c in obj_category:
                    if obj_matches(c, key):
                        return c.get(match_key, False)
        return False

    def is_hidden(self, name, category=None, key=None):
        return self.match_object(name, 'hidden', category, key)

    def is_skipped(self, name, category=None, key=None):
        if self.is_hidden(name, category, key):
            return True
        return self.match_object(name, 'check_ignore', category, key)

    def is_unstable(self, version):
        if not version:
            return False
        cur_version = self.library.get('version')
        if cur_version is None:
            return False

        return packaging_version.parse(version) > packaging_version.parse(cur_version)

    @property
    def generator(self):
        return f"{core.version}"

    @property
    def favicons(self):
        if not self._favicons:
            self._favicons = [
                os.path.basename(p)
                for p in self.content_images
                if os.path.basename(p).startswith('favicon')
            ]

        return self._favicons

    @property
    def ignore_deprecated(self):
        return self.check.get('ignore_deprecated', False)


class GITemplateConfig:
    """Load and represent the template configuration"""
    def __init__(self, templates_dir, template_name):
        self._templates_dir = templates_dir
        self._template_name = template_name
        self._config_file = os.path.join(templates_dir, template_name, f"{template_name}.toml")

        self._config = {}
        log.debug(f"Reading template configuration file: {self._config_file}")
        self._config = TomlConfig.load(self._config_file)

    @property
    def name(self):
        metadata = self._config.get('metadata', {})
        return metadata.get('name', self._template_name)

    @property
    def css(self):
        css = self._config.get('css', {})
        return css.get('style', None)

    @property
    def extra_files(self):
        extra = self._config.get('extra_files', {})
        return extra.get('files', [])

    @property
    def templates(self):
        return self._config.get('templates', {})

    @property
    def class_template(self):
        return self.templates.get('class', 'class.html')

    @property
    def method_template(self):
        return self.templates.get('method', 'method.html')

    @property
    def class_method_template(self):
        return self.templates.get('class_method', 'class_method.html')

    @property
    def vfunc_template(self):
        return self.templates.get('vfunc', 'vfunc.html')

    @property
    def property_template(self):
        return self.templates.get('property', 'property.html')

    @property
    def signal_template(self):
        return self.templates.get('signal', 'signal.html')

    @property
    def type_func_template(self):
        return self.templates.get('type_func', 'type_func.html')

    @property
    def ctor_template(self):
        return self.templates.get('ctor', 'type_func.html')

    @property
    def func_template(self):
        return self.templates.get('function', 'function.html')

    @property
    def constant_template(self):
        return self.templates.get('constant', 'constant.html')

    @property
    def interface_template(self):
        return self.templates.get('interface', 'interface.html')

    @property
    def namespace_template(self):
        return self.templates.get('namespace', 'namespace.html')

    @property
    def content_template(self):
        return self.templates.get('content', 'content.html')

    @property
    def enum_template(self):
        return self.templates.get('enum', 'enum.html')

    @property
    def flags_template(self):
        return self.templates.get('flags', 'flags.html')

    @property
    def error_template(self):
        return self.templates.get('error', 'error.html')

    @property
    def record_template(self):
        return self.templates.get('record', 'record.html')

    @property
    def union_template(self):
        return self.templates.get('union', 'union.html')

    @property
    def alias_template(self):
        return self.templates.get('alias', 'alias.html')
