[app]
title = Jarvis
package.name = jarvis
package.domain = com.shutnk

source.dir = src
source.include_exts = py,kv,json,png,jpg,ttf
source.include_patterns = assets/*

version = 0.1.0
requirements = python3==3.11,kivy==2.2.1,requests,urllib3,certifi,chardet,idna

orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 24
android.ndk = 25b
android.sdk = 34
android.archs = arm64-v8a
android.allow_backup = True
android.permissions = INTERNET,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE

android.release_artifact = aab
android.debug_artifact = apk

p4a.branch = develop
[buildozer]
log_level = 2
warn_on_root = 1
