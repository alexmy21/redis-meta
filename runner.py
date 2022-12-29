import importlib

mod = importlib.import_module('.hello', package='meta-app')
mod.greet()