# -*- coding: utf-8 -*-
import os
import re
import sys
import yaml

from lektor.pluginsystem import Plugin
from lektor.publisher import Publisher, Command


class GaePublisher(Publisher):
    def write_301(self):
        # 301 redirect to canonical URLs with trailing slash
        target = os.path.join(self.output_path, "301.php")
        with open(target, "w") as file:
            file.write("<?php header('Location: http://'.$_SERVER['HTTP_HOST'].strtok($_SERVER['REQUEST_URI'],'?').'/', TRUE, 301); ?>")
        return True

    def write_404(self):
        # 404 response code with custom error page
        if not os.path.isfile(os.path.join(self.output_path, "404.html")):
            return False
        target = os.path.join(self.output_path, "404.php")
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
            "url": "/" + re.escape(remote_path),
            "static_files": local_path.replace("\\", "\\\\"),
            "upload": re.escape(local_path),
            "http_headers": {
                "Vary": "Accept-Encoding",
            },
        }
        
    def find_sdk(self):
        for path in os.environ['PATH'].split(os.pathsep):
            cmd = os.path.join(path, 'appcfg.py')
            if os.path.isfile(cmd):
                return cmd
        raise RuntimeError('Could not locate Google App Engine SDK.')
        
    def publish(self, target_url, credentials=None, **extra):
        # Initialize the app; default to version 1 if not specified
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
            # Force use of forward slashes for app engine
            local_path = "/".join(path.split(os.path.sep))
            remote_path = local_path
            if os.path.basename(local_path) == "index.html":
                # Strip off the index.html
                remote_path = os.path.dirname(remote_path)
                if remote_path != "":
                    # Add 301 redirects to canonical URLs
                    remote_path = remote_path + "/"
                    app["handlers"].append({
                        "url": "/" + re.escape(os.path.dirname(remote_path)),
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
        target = os.path.join(self.output_path, "app.yaml")
        with open(target, "w") as file:
            file.write(yaml.dump(app))

        cmd = self.find_sdk()
        for line in Command([sys.executable, cmd, 'update', self.output_path]):
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
