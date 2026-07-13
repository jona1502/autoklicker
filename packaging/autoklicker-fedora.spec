%global app_version 1.1.4

Name:           autoklicker
Version:        %{app_version}
Release:        1%{?dist}
Summary:        AutoKlicker with hotkeys and recording support

License:        LicenseRef-Proprietary-Freeware
URL:            https://github.com/jona1502/autoklicker
Source0:        autoklicker
Source1:        autoklicker.desktop
Source2:        autoklicker.png

ExclusiveArch:  x86_64
Requires:       libX11
Requires:       libXtst

%description
AutoKlicker is a desktop auto-clicker built with Python and tkinter. This
package installs the PyInstaller-built Linux executable, desktop entry, and
application icon.

%prep

%build

%install
install -D -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/autoklicker
install -D -m 0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/autoklicker.desktop
install -D -m 0644 %{SOURCE2} %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/autoklicker.png

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/autoklicker.desktop

%files
%{_bindir}/autoklicker
%{_datadir}/applications/autoklicker.desktop
%{_datadir}/icons/hicolor/256x256/apps/autoklicker.png

%changelog
* Mon Jul 13 2026 AutoKlicker Maintainers <noreply@example.com> - 1.1.4-1
- Add Fedora RPM release package.
