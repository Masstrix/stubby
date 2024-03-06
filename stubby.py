"""
stubby.py - A Python script to generate stub files for Python modules.

Copyright (C) 2024 Matthew Denton

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Github: https://github.com/Masstrix/stubby
Author: Matthew Denton
"""

import inspect
import os
import importlib
import pkgutil
import shutil


class ModuleStubGenerator:

    def __init__(self, obj):
        self._obj = obj
        self._members = inspect.getmembers(obj)

    def generate(self, output_folder: str):
        package = str(self._obj.__package__)
        module_name = str(self._obj.__name__).removeprefix(f'{package}.')
        output_file = os.path.join(output_folder, *package.split('.'), f'{module_name}.pyi')
        root_folder = os.path.dirname(output_file)

        if not os.path.exists(root_folder):
            os.makedirs(root_folder)

        with open(output_file, 'w') as f:
            f.write(f"# Auto generatded stub from stubby.py {self._obj.__name__}\n\n")

            for name, member in self._members:
                if name.startswith('__'):
                    continue

                if inspect.isclass(member):
                    f.write(f"class {name}:\n    ...")
                elif inspect.isfunction(member):

                    f.write(f"def {name}{str(inspect.signature(member))}: ...")
                elif inspect.ismodule(member):
                    f.write(f"import {member.__name__}  # type: ignore")
                elif inspect.isbuiltin(member):
                    f.write(f"# Built-in: {name}")
                else:
                    obj_type = type(member).__name__
                    obj_module = obj_type.__class__.__module__
                    obj_type = None if obj_type == 'NoneType' else obj_type

                    is_builtin = obj_module == 'builtins'

                    f.write(f"{name}: {obj_type} # builtin: {obj_module} {is_builtin}")

                f.write('\n\n')


class StubGenerator:

    def __init__(self, obj):
        self.module = obj

    def generate(self, output_folder: str, flush_old: bool = False):
        """Generates the stub files.
        
        Args:
            output_folder (str): Where to put the stub files to.
            flush_old (bool, optional): When enabled all old stubs will be fist deleted.
                to make sure they are the latest.
        """
        if flush_old and os.path.exists(output_folder):
            shutil.rmtree(output_folder)

        self._generate_stubs(self.module, output_folder)

    def _generate_stubs(self, module, output_folder, _package: str = None):
        # Set the package
        if _package == None:
            _package = module.__package__

        # Go over all the modules in this package and generat a stub for them.
        # If any of them are packages then they will revusivly call this.
        modinfo: pkgutil.ModuleInfo
        for modinfo in pkgutil.iter_modules(module.__path__, f'{_package}.'):
            loaded = importlib.import_module(modinfo.name)

            # Load a new package
            if modinfo.ispkg:
                self._generate_stubs(loaded, output_folder, f'{loaded.__package__}')
                continue

            # Generate a stub file for the module
            generator = ModuleStubGenerator(loaded)
            generator.generate(output_folder)


def main():
    import stubbytest as stubbytest

    root = os.path.dirname(__file__)

    # Generate a stub from the test setup
    generator = StubGenerator(stubbytest)
    generator.generate(os.path.join(root, 'dist', 'stubs'), True)


if __name__ == '__main__':
    main()