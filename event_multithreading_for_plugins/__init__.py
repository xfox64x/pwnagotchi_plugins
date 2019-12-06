import os
import queue
import threading
import glob
import importlib, importlib.util
import logging
import time

default_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "default")
loaded = {}
exitFlag = 0
plugin_event_queues = {}

def dummy_callback():
    pass

class WorkerThread (threading.Thread):
    def __init__(self, plugin_name, event_name, work_queue):
        threading.Thread.__init__(self)
        self.plugin_name = plugin_name
        self.event_name = event_name
        self.work_queue = work_queue

    def run(self):
        logging.info("Worker thread starting for %s.%s"%(self.plugin_name, self.event_name))
        process_event(self.plugin_name, self.event_name, self.work_queue)
        logging.info("Worker thread exiting for %s.%s"%(self.plugin_name, self.event_name))


def process_event(plugin_name, event_name, work_queue):
    while not exitFlag:
        plugin_event_queues[plugin_name][event_name].queue_lock.acquire()
        if not work_queue.empty():
            data = work_queue.get()
            plugin_event_queues[plugin_name][event_name].queue_lock.release()
            try:
                loaded[plugin_name].__dict__[('on_%s'%event_name)](*data[0], **data[1])
            except Exception as e:
                logging.error("error while running %s.%s : %s" % (plugin_name, event_name, e))
        else:
            plugin_event_queues[plugin_name][event_name].queue_lock.release()
            time.sleep(1)


class PluginEventQueue():
    def __init__(self, plugin_name, event_name):
        self.plugin_name = plugin_name
        self.event_name = event_name
        self.work_queue = queue.Queue()
        self.worker_thread = WorkerThread(self.plugin_name, self.event_name, self.work_queue)
        self.queue_lock = threading.Lock()
        self.worker_thread.start()

    def AddWork(self, *args, **kwargs):
        self.queue_lock.acquire()
        self.work_queue.put([args, kwargs])
        self.queue_lock.release()


def on(event_name, *args, **kwargs):
    global loaded
    global plugin_event_queues
    cb_name = 'on_%s' % event_name
    for plugin_name, plugin in loaded.items():
        if cb_name not in plugin.__dict__:
            continue
        
        if plugin_name not in plugin_event_queues:
            plugin_event_queues[plugin_name] = {}

        if event_name not in plugin_event_queues[plugin_name]:
            plugin_event_queues[plugin_name][event_name] = PluginEventQueue(plugin_name, event_name)

        plugin_event_queues[plugin_name][event_name].AddWork(*args, **kwargs)


def load_from_file(filename):
    plugin_name = os.path.basename(filename.replace(".py", ""))
    spec = importlib.util.spec_from_file_location(plugin_name, filename)
    instance = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(instance)
    return plugin_name, instance


def load_from_path(path, enabled=()):
    global loaded
    for filename in glob.glob(os.path.join(path, "*.py")):
        name, plugin = load_from_file(filename)
        if name in loaded:
            raise Exception("plugin %s already loaded from %s" % (name, plugin.__file__))
        elif name not in enabled:
            # print("plugin %s is not enabled" % name)
            pass
        else:
            loaded[name] = plugin

    return loaded


def load(config):
    enabled = [name for name, options in config['main']['plugins'].items() if 'enabled' in options and options['enabled']]
    custom_path = config['main']['custom_plugins'] if 'custom_plugins' in config['main'] else None
    # load default plugins
    loaded = load_from_path(default_path, enabled=enabled)
    # set the options
    for name, plugin in loaded.items():
        plugin.__dict__['OPTIONS'] = config['main']['plugins'][name]
    # load custom ones
    if custom_path is not None:
        loaded = load_from_path(custom_path, enabled=enabled)
        # set the options
        for name, plugin in loaded.items():
            plugin.__dict__['OPTIONS'] = config['main']['plugins'][name]

    on('loaded')
