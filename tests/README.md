### Setting the PYTHONPATH environment variable for testing

The `PYTHONPATH` environment variable needs to be set before running tests because otherwise we will run into `ImportErrors` in the main application.

This is due to the fact that some imports were not working properly so I had to modify `sys.path` in order to make them work.

The `PYTHONPATH` environment variable should be set as follows (assuming you are in the root directory of the application):

#### Linux

```bash
Path=$(pwd)/enosimulator
export PYTHONPATH=$PYTHONPATH:..:../..:$Path
```

#### Windows

```bash
$Path = Join-Path (Get-Location) "enosimulator"
$env:PYTHONPATH += '..;../..;'
$env:PYTHONPATH += $Path
```
