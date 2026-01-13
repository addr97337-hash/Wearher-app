[app]
title = Weather App
package.name = weatherapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,kivymd,requests,urllib3,openssl
orientation = portrait
fullscreen = 1
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.sdk = 20
android.ndk = 25b
android.entrypoint = org.kivy.android.PythonActivity
android.enable_androidx = True
android.archs = arm64-v8a
android.allow_backup = True
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
