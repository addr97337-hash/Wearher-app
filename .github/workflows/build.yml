name: Build
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Build with Buildozer
        uses: ArtemSBulgakov/buildozer-action-v1@v1
        id: buildozer
        with:
          command: buildozer android debug
          buildozer_version: master

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: WeatherApp-APK
          path: ${{ steps.buildozer.outputs.filename }}
          
