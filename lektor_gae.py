# -*- coding: utf-8 -*-
import os
import yaml
import shutil
import tempfile

from lektor.pluginsystem import Plugin
from lektor.publisher import Publisher, Command


class GaePublisher(Publisher):
    def __init__(self, env, output_path):
        super(GaePublisher, self).__init__(env, output_path)
        self.temp_path = tempfile.mkdtemp()

    def __del__(self):
        shutil.rmtree(self.temp_path)

    def write_301(self):
        # 301 redirect to canonical URLs with trailing slash
        target = os.path.join(self.temp_path, "301.php")
        with open(target, "w") as file:
            file.write("<?php header('Location: ' + strtok($_SERVER['REQUEST_URI'],'?') + '/', TRUE, 301); ?>")
        return True

    def write_404(self):
        # 404 response code with custom error page
        if not os.path.isfile(os.path.join(self.output_path, "404.html")):
            return False
        target = os.path.join(self.temp_path, "404.php")
        with open(target, "w") as file:
            file.write("<?php http_response_code(404); require('404.html'); ?>")
        return True

    def get_files(self):
        # Get list of output files
        all_files = []
        for root, dirs, files in os.walk(self.output_path):
            files   = [f for f in files if not f[0] == "."]
            dirs[:] = [d for d in dirs  if not d[0] == "."]
            for f in files:
                fullpath = os.path.join(root, f)
                relpath = os.path.relpath(fullpath, self.output_path)
                if relpath != "404.html":
                    all_files.append(relpath)
        return all_files

    def gen_handler(self, remote_path, local_path):
        # Generate a URL handler
        return {
            "url": remote_path.replace(".", "\\."),
            "static_files": local_path,
            "upload": local_path.replace(".", "\\."),
            "http_headers": {
                "Vary": "Accept-Encoding",
            },
        }

    def publish(self, target_url, credentials=None, **extra):
        # Initialize the app
        (empty, application, version) = os.path.split(str(target_url.path)) + (1,)
        app = {
            "application": application,
            "version": version,
            "runtime": 'php55',
            "api_version": 1,
            "handlers" : [],
        }

        # Add a handler for each static page
        for path in self.get_files():
            local_path = os.path.join(self.temp_path, path)
            remote_path = "/".join([""] + path.split(os.path.sep))
            if os.path.basename(local_path) == "index.html":
                # Strip off the index.html
                remote_path = os.path.dirname(remote_path)
                if remote_path != "/":
                    # Add 301 redirects to canonical URLs
                    remote_path = remote_path + "/"
                    app["handlers"].append({
                        "url": os.path.dirname(remote_path).replace(".", "\\."),
                        "script": "301.php",
                    })
            app["handlers"].append(self.gen_handler(remote_path, local_path))

        # Create PHP handlers
        self.write_301()
        if self.write_404():
            app["handlers"].append({
                "url": "/.*",
                "script": "404.php",
            })

        # Generate the YAML
        target = os.path.join(self.temp_path, "app.yaml")
        with open(target, "w") as file:
            file.write(yaml.dump(app))

        # TODO: Find the Google App Engine SDK
        for line in Command(['python', r'C:\Program Files (x86)\Google\google_appengine\appcfg.py', 'update', self.temp_path]):
            yield line


class GaePlugin(Plugin):
    name = u"Google App Engine"
    description = u"Publishes your Lektor site to Google App Engine."

    def on_setup_env(self, **extra):
        scheme = "gae";
        if hasattr(self.env, "publishers"):
            self.env.add_publisher(scheme, GaePublisher)
        else:
            from lektor.publisher import publishers
            publishers[scheme] = GaePublisher
