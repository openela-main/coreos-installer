# Generated by rust2rpm 13
%define dracutlibdir %{_prefix}/lib/dracut
%bcond_without check
%global __cargo_skip_build 0
# The library is for internal code reuse and is not a public API
%global __cargo_is_lib 0

%global coidracutcommit 89d5789ef30ee35c7d083f425c7a083459989dbd
%global coidracutshortcommit %(c=%{coidracutcommit}; echo ${c:0:7})

%global crate coreos-installer

Name:           %{crate}
Version:        0.15.0
Release:        2%{?dist}
Summary:        Installer for Fedora CoreOS and RHEL CoreOS

# Upstream license specification: Apache-2.0
License:        ASL 2.0
URL:            https://github.com/coreos/coreos-installer
Source:         https://crates.io/api/v1/crates/%{crate}/%{version}/download#/%{crate}-%{version}.crate
Source1:        https://github.com/coreos/coreos-installer/releases/download/v%{version}/%{crate}-%{version}-vendor.tar.gz
Source2:	https://github.com/runcom/coreos-installer-dracut/archive/%{coidracutcommit}/coreos-installer-dracut-%{coidracutshortcommit}.tar.gz

# The RHEL 8 rust-toolset macros don't let us enable features from the
# %%cargo_* macros.  Enable rdcore directly in Cargo.toml.
Patch0:         enable-rdcore.patch

ExclusiveArch:  %{rust_arches}
BuildRequires:  openssl-devel
# To ensure we're not bundling system libraries
BuildRequires:  xz-devel
BuildRequires:  rust-toolset
BuildRequires:  systemd
BuildRequires:  gnupg2

Requires:       gnupg
Requires:       kpartx
Requires:       systemd-udev
Requires:       util-linux
%ifarch s390x
# This should eventually be spelled "s390utils-core" but the binaries
# haven't been broken out of s390utils-base yet
Requires:       /usr/sbin/chreipl
Requires:       /usr/sbin/dasdfmt
Requires:       /usr/sbin/fdasd
Requires:       /usr/sbin/lszdev
Requires:       /usr/sbin/zipl
%endif

# Since `rust-coreos-installer` creates a `coreos-installer`
# subpackage with a newer version number, which supersedes the
# deprecated `coreos-installer` package (https://src.fedoraproject.org/rpms/coreos-installer),
# an explicit `Obsoletes:` for `coreos-installer` is not necessary.

%global _description %{expand:
coreos-installer installs Fedora CoreOS or RHEL CoreOS to bare-metal
machines (or, occasionally, to virtual machines).
}
%description %{_description}

%prep
%autosetup -n %{crate}-%{version} -p1
%setup -D -T -a 2
%cargo_prep -V 1
# https://github.com/rust-lang-nursery/error-chain/pull/289
find -name '*.rs' -executable -exec chmod a-x {} \;

%build
%cargo_build

%install
%make_install RELEASE=1
# 51coreos-installer for coreos-installer-dracut
%make_install -C coreos-installer-dracut-%{coidracutcommit}

%package     -n %{crate}-bootinfra
Summary:     %{crate} boot-time infrastructure for use on Fedora/RHEL CoreOS
Requires:   %{crate} = %{version}-%{release}

# Package was renamed from coreos-installer-systemd when rdcore was added
Provides:    %{crate}-systemd = %{version}-%{release}
Obsoletes:   %{crate}-systemd <= 0.3.0-2

%description -n %{crate}-bootinfra
This subpackage contains boot-time infrastructure for Fedora CoreOS and
RHEL CoreOS.  It is not needed on other platforms.

%files       -n %{crate}-bootinfra
%{dracutlibdir}/modules.d/50rdcore/*
%{_libexecdir}/*
%{_unitdir}/*
%{_systemdgeneratordir}/*

%package     -n %{crate}-dracut
Summary:     %{crate} provides coreos-installer as a dracut module.
Requires:   %{crate} = %{version}-%{release}

%description -n %{crate}-dracut
This subpackage contains files and configuration to run coreos-installer
from the initramfs.

%files       -n %{crate}-dracut
%{dracutlibdir}/modules.d/51coreos-installer/*

%files       -n %{crate}
%license LICENSE
%doc README.md
%{_bindir}/coreos-installer
%{_mandir}/man8/*

%if %{with check}
%check
%cargo_test
%endif

%changelog
* Mon Sep 05 2022 Antonio Murdaca <runcom@linux.com> - 0.15.0-2
- revert bump coi-dracut, 8.7 won't support growing LVM

* Mon Aug 22 2022 Antonio Murdaca <runcom@linux.com> - 0.15.0-1
- bump to 0.15.0
- bump coi-dracut to support LVM backed images

* Thu Feb 24 2022 Antonio Murdaca <runcom@linux.com> - 0.11.0-3
- update coi-dracut to fix growfs service Before

* Thu Feb 10 2022 Antonio Murdaca <runcom@linux.com> - 0.11.0-2
- update coi-dracut to support default poweroff behavior

* Wed Feb 02 2022 Antonio Murdaca <runcom@linux.com> - 0.11.0-1
- bump to 0.11.0 and support luks in -dracut

* Thu Nov 18 2021 Antonio Murdaca <runcom@linux.com> - 0.10.1-2
- fix dracut module dependencies

* Wed Oct 13 2021 Antonio Murdaca <runcom@linux.com> - 0.10.1-1
- bump to 0.10.1
- bump coreos-installer-dracut

* Thu Sep 9 2021 Antonio Murdaca <runcom@redhat.com> - 0.9.1-19
- add a new coreos-installer-dracut subpkg to include just the
  dracut module (fedora-iot/coreos-installer-dracut)

* Tue Aug 31 2021 Jan Schintag <jschinta@redhat.com> - 0.10.0-1
- Bump version to 0.10.0

* Mon Jun 21 2021 Jonathan Lebon <jlebon@redhat.com> - 0.9.1-4
- Add xz-devel BR to ensure we're not bundling
  Related: https://bugzilla.redhat.com/show_bug.cgi?id=1974453

* Thu Jun 10 2021 Benjamin Gilbert <bgilbert@redhat.com> - 0.9.1-3
- Support s390x DASDs in VMs via virtio

* Tue Jun 08 2021 Dusty Mabe <dustymabe@redhat.com> - 0.9.1-2
- Add coreos.force_persist_ip karg forwarding

* Wed Apr 21 2021 Benjamin Gilbert <bgilbert@redhat.com> - 0.9.0-3
- Improve error message for busy disk referenced via symlink
- Fix failure on corrupt GPT

* Fri Apr 9 2021 Sohan Kunkerkar <skunkerk@redhat.com> - 0.9.0-2
- Use macro for dracut library path

* Thu Apr 8 2021 Sohan Kunkerkar <skunkerk@redhat.com> - 0.9.0-1
- New release

* Fri Jan 15 2021 Benjamin Gilbert <bgilbert@redhat.com> - 0.8.0-3
- Fix rdcore rootmap on RAID devices

* Tue Jan 12 2021 Benjamin Gilbert <bgilbert@redhat.com> - 0.8.0-2
- Disable LTO again to avoid crashes on s390x

* Tue Jan 12 2021 Sohan Kunkerkar <skunkerk@redhat.com> - 0.8.0-1
- New release

* Mon Jan 04 2021 Benjamin Gilbert <bgilbert@redhat.com> - 0.7.2-2
- Add Requires for programs invoked by coreos-installer
- Require Rust >= 1.45, re-enable LTO

* Thu Oct 22 2020 Sohan Kunkerkar <skunkerk@redhat.com> - 0.7.2-1
- New release

* Mon Sep 21 2020 Benjamin Gilbert <bgilbert@redhat.com> - 0.6.0-3
- Fix MBR handling when partition saving is enabled
- Fix base package Obsoletes being interpreted as part of package description

* Wed Sep 02 2020 Benjamin Gilbert <bgilbert@redhat.com> - 0.6.0-2
- Disable LTO on s390x to avoid runtime crashes
- Drop legacy installer

* Tue Aug 25 2020 Benjamin Gilbert <bgilbert@redhat.com> - 0.6.0-1
- New release

* Fri Jul 31 2020 Benjamin Gilbert <bgilbert@redhat.com> - 0.5.0-1
- New release

* Sat Jul 25 2020 Benjamin Gilbert <bgilbert@redhat.com> - 0.4.0-1
- New release
- Rename -systemd subpackage to -bootinfra
- Add rdcore Dracut module to -bootinfra

* Wed Jul 22 2020 Benjamin Gilbert <bgilbert@redhat.com> - 0.3.0-1
- New release
- Make coreos-installer-{service,generator} world-readable

* Wed Jun 17 2020 Dusty Mabe <dusty@dustymabe.com> - 0.2.0-4.rhaos4.6
- Include rhaos4.6 in the rpm release field

* Thu May 28 2020 Colin Walters <walters@verbum.org> - 0.2.0-3
- Backport osmet RHCOS+LUKS patches

* Thu May 07 2020 Dusty Mabe <dusty@dustymabe.com> - 0.2.0-2
- Fix bug in dracut hook in legacy installer; see
  https://github.com/coreos/coreos-installer/pull/234

* Mon Apr 27 2020 Colin Walters <walters@verbum.org> - 0.1.3-4
- Merge in legacy installer; see
  https://github.com/coreos/coreos-installer/pull/220

* Mon Mar 23 2020 Colin Walters <walters@verbum.org> - 0.1.3-2
- https://github.com/coreos/coreos-installer/releases/tag/v0.1.3

* Wed Mar 04 2020 Colin Walters <walters@verbum.org> - 0.1.2-11
- Backport no-signatures-available patch

* Wed Feb 26 2020 Colin Walters <walters@verbum.org> - 0.1.2-10
- Forked from Fedora
- I forgot about the weird `rust-` package name prefixing when
  asking RCM to make the dist-git repo, and rather than redo
  that I decided to just go with it.
- Stop depending on systemd-rpm-macros since it's not in RHEL8 apparently
- Drop other things only applicable to Fedora Rust packaging like
  dynamic buildrequires
