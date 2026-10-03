[app]
title = Jarvis
package.name = jarvis
package.domain = com.shutnk

source.dir = src
source.include_exts = py,kv,json,png,jpg,ttf,mp3
source.include_patterns = assets/*

version = 0.1.0
# Keep the Android interpreter compatible with Kivy 2.3.1. The workflow
# patches the p4a recipes so hostpython3 and python3 use this same version.
requirements = python3,kivy==2.3.1,pyjnius

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
log_level = 2
warn_on_root = 0
