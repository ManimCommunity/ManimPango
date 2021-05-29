param($output)
$ErrorActionPreference = 'Stop'
if (Test-Path -Path $output){
    Write-Output "File alread Exists. Exiting."
    exit 0
}
$currentloc = $PWD
$host_arch = "amd64"
$arch = "amd64"
Set-Location $env:TEMP
Write-Output "Getting pkg-config"
Invoke-WebRequest https://github.com/pkgconf/pkgconf/archive/pkgconf-1.7.0.zip -o pkgconf.zip
7z x pkgconf.zip
Move-Item -Path pkgconf-* -Destination pkgconf -Force
$installationPath = vswhere.exe -prerelease -latest -property installationPath
if ($installationPath -and (test-path "$installationPath\Common7\Tools\vsdevcmd.bat")) {
    & "${env:COMSPEC}" /s /c "`"$installationPath\Common7\Tools\vsdevcmd.bat`" -no_logo -host_arch=$host_arch -arch=$arch && set" | foreach-object {
        $name, $value = $_ -split '=', 2
        set-content env:\"$name" $value
    }
}
pip install --upgrade meson==0.55.3 ninja
$env:PKG_CONFIG_PATH=""
meson setup --prefix=$output --buildtype=release -Dtests=false pkg_conf_build pkgconf
meson compile -C pkg_conf_build
meson install --no-rebuild -C pkg_conf_build
Rename-Item $output\bin\pkgconf.exe $output\bin\pkg-config.exe -Force
Set-Location $currentloc
