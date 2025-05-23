# asconnect

asconnect is a Python wrapper around the [Apple App Store Connect REST APIs](https://developer.apple.com/documentation/appstoreconnectapi).

This wrapper does not cover every API, but does cover the basics, including:

* Uploading a build
* Creating a new TestFlight version
* Setting TestFlight review information
* Creating a new app store version
* Setting the app review information
* Submitting for app review

## Getting Started

### Installation

The package is available on PyPI, so you can run `pip install asconnect` to get the latest version.

### Creating a client

To begin, you need to [generate a key](https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api), then get it's ID, the contents of the key itself, and the issuer ID.

Once you have those, you can create a new client by running:

```python
client = asconnect.Client(key_id="...", key_contents="...", issuer_id="...")
```

### Getting your App

Most operations require an app identifier. This is not the same as the bundle ID you choose, but is an ID generated by Apple. The easiest way to get this is to run this code:

```python
app = client.app.get_from_bundle_id("com.example.my_bundle_id")
```

### Uploading a Build

Uploading a build isn't technically part of the App Store Connect APIs, but a wrapper around altool is included to make things as easy as possible. Let's upload a build for your app:

```python
client.build.upload(
  ipa_path="/path/to/the/app.ipa",
  platform=asconnect.Platform.ios,
)
```

And if you want to wait for your build to finish processing:

```python
build = client.build.wait_for_build_to_process("com.example.my_bundle_id", build_number)
```

`build_number` is the build number you gave your build when you created it. It's used by the app store to identify the build.

### App Store Submission

Let's take that build, create a new app store version and submit it,

```python
# Create a new version
version = client.app.create_new_version(version="1.2.3", app_id=app.identifier)

# Set the build for that version
client.version.set_build(version_id=version.identifier, build_id=build.identifier)

# Submit for review
client.version.submit_for_review(app_id=app.identifier, platform=Platform.IOS)
```

It's that easy. Most of the time at least. If you don't have previous version to inherit information from you'll need to do things like set screenshots, reviewer info, etc. All of which is possible through this library.
### Phased Distribution
```python
# Create a new version
version = client.app.create_new_version(version="1.2.3", app_id=app.identifier)

# Start a versions' phased release, the initial state of which is INACTIVE
phased_release = client.version.create_phased_release(version_id=version.identifier)

# Check on a phased release
phased_release = client.version.get_phased_release(version_id=version.identifier)

# Advance or modify a phased release
phased_release = client.version.patch_phased_release(phased_release_id=phased_release.identifier, phased_release_state=PhasedReleaseState.active)
phased_release = client.version.patch_phased_release(phased_release_id=phased_release.identifier, phased_release_state=PhasedReleaseState.pause)
phased_release = client.version.patch_phased_release(phased_release_id=phased_release.identifier, phased_release_state=PhasedReleaseState.complete)

# Delete
client.version.delete_phased_release(phased_release_id=phased_release.identifier)
```
# Getting Started

For development `asconnect` uses [`poetry`](https://github.com/python-poetry/poetry)

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
