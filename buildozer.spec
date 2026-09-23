[app]
title = Jarvis
package.name = jarvis
package.domain = com.shutnk

source.dir = src
source.include_exts = py,kv,json,png,jpg,ttf
source.include_patterns = assets/*

version = 0.1.0
requirements = python3,kivy==2.3.1,requests

orientation = portrait
fullscreen = 0
android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.allow_backup = True
android.permissions = INTERNET,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE

android.release_artifact = aab
android.debug_artifact = apk

[buildozer]
log_level = 1
warn_on_root = 1
android.python_version = 3.11
p4a.branch = master
p4a.extra_args = --python-version=3.11
