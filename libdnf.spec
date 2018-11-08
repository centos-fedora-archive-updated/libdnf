%global libsolv_version 0.6.21-1
%global dnf_conflict 2.7.2

%bcond_with valgrind

# Do not build bindings for python3 for RHEL <= 7
%if 0%{?rhel} && 0%{?rhel} <= 7
%bcond_with python3
%else
%bcond_without python3
%endif

%if 0%{?rhel} && 0%{!?centos}
%bcond_without rhsm
%else
%bcond_with rhsm
%endif

%global _cmake_opts \\\
    -DENABLE_RHSM_SUPPORT=%{?with_rhsm:ON}%{!?with_rhsm:OFF} \\\
    %{nil}

Name:           libdnf
Version:        0.11.1
Release:        6%{?dist}
Summary:        Library providing simplified C and Python API to libsolv
License:        LGPLv2+
URL:            https://github.com/rpm-software-management/libdnf
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz
Patch0001:      0001-Use-arch-from-spec-in-hy_subject_get_best_selector-RhBug1542307.patch
Patch0002:      0002-Fix-segfault-in-repo_internalize_trigger-RhBug1375895.patch
Patch0003:      0003-Fix-memory-corruption-in-dnf_context.patch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  libsolv-devel >= %{libsolv_version}
BuildRequires:  pkgconfig(librepo)
BuildRequires:  pkgconfig(check)
%if %{with valgrind}
BuildRequires:  valgrind
%endif
BuildRequires:  pkgconfig(gio-unix-2.0) >= 2.46.0
BuildRequires:  pkgconfig(gtk-doc)
BuildRequires:  pkgconfig(gobject-introspection-1.0)
BuildRequires:  rpm-devel >= 4.11.0
%if %{with rhsm}
BuildRequires:  pkgconfig(librhsm)
%endif

Requires:       libsolv%{?_isa} >= %{libsolv_version}

%description
A Library providing simplified C and Python API to libsolv.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libsolv-devel%{?_isa} >= %{libsolv_version}

%description devel
Development files for %{name}.

%package -n python2-hawkey
Summary:        Python 2 bindings for the hawkey library
%{?python_provide:%python_provide python2-hawkey}
BuildRequires:  python2-devel
%if 0%{?rhel} && 0%{?rhel} <= 7
BuildRequires:  python-nose
%else
BuildRequires:  python2-nose
%endif
Requires:       %{name}%{?_isa} = %{version}-%{release}
# Fix problem with hawkey - dnf version incompatibility
# Can be deleted for distros where only python2-dnf >= 2.0.0
Conflicts:      python2-dnf < %{dnf_conflict}
Conflicts:      python-dnf < %{dnf_conflict}

%description -n python2-hawkey
Python 2 bindings for the hawkey library.

%if %{with python3}
%package -n python3-hawkey
Summary:        Python 3 bindings for the hawkey library
%{?python_provide:%python_provide python3-hawkey}
BuildRequires:  python3-devel
BuildRequires:  python3-nose
Requires:       %{name}%{?_isa} = %{version}-%{release}
# Fix problem with hawkey - dnf version incompatibility
# Can be deleted for distros where only python3-dnf >= 2.0.0
Conflicts:      python3-dnf < %{dnf_conflict}
Obsoletes:      platform-python-hawkey < %{version}-%{release}

%description -n python3-hawkey
Python 3 bindings for the hawkey library.
%endif

%prep
%autosetup -p1
mkdir build-py2
%if %{with python3}
mkdir build-py3
%endif

%build
pushd build-py2
  %cmake -DWITH_MAN=OFF ../ %{!?with_valgrind:-DDISABLE_VALGRIND=1} %{_cmake_opts}
  %make_build
popd

%if %{with python3}
pushd build-py3
  %cmake -DPYTHON_DESIRED:str=3 -DWITH_GIR=0 -DWITH_MAN=0 -Dgtkdoc=0 ../ %{!?with_valgrind:-DDISABLE_VALGRIND=1} %{_cmake_opts}
  %make_build
popd
%endif

%check
if [ "$(id -u)" == "0" ] ; then
        cat <<ERROR 1>&2
Package tests cannot be run under superuser account.
Please build the package as non-root user.
ERROR
        exit 1
fi
pushd build-py2
  make ARGS="-V" test
popd
%if %{with python3}
# Run just the Python tests, not all of them, since
# we have coverage of the core from the first build
pushd build-py3/python/hawkey/tests
  make ARGS="-V" test
popd
%endif

%install
pushd build-py2
  %make_install
popd
%if %{with python3}
pushd build-py3
  %make_install
popd
%endif

%ldconfig_scriptlets

%files
%license COPYING
%doc README.md AUTHORS NEWS
%{_libdir}/%{name}.so.*
%{_libdir}/girepository-1.0/Dnf-*.typelib

%files devel
%doc %{_datadir}/gtk-doc/html/%{name}/
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/%{name}/
%{_datadir}/gir-1.0/Dnf-*.gir

%files -n python2-hawkey
%{python2_sitearch}/hawkey/

%if %{with python3}
%files -n python3-hawkey
%{python3_sitearch}/hawkey/
%endif

%changelog
* Thu Nov 08 2018 aroslav Mracek <jmracek@redhat.com> - 0.11.1-6
- Backport patches from upstream libdnf-0.11.1

* Sat Nov 03 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.11.1-5.1
- Rebuild for libsolv 0.7

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Jan 30 2018 Igor Gnatenko <ignatenko@redhat.com> - 0.11.1-4
- Switch to %%ldconfig_scriptlets

* Tue Nov 07 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.11.1-3
- Use better Obsoletes for platform-python

* Fri Nov 03 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.11.1-2
- Remove platform-python subpackage

* Mon Oct 16 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.11.1-1
- Rerelease of 0.11.1-1
- Improvement query performance
- Run file query in hy_subject_get_best_solution only for files (arguments that start with ``/`` or
  ``*/``)
- Resolves: rhbz#1498207 - DNF crash during upgrade installation F26 -> F27

* Tue Oct 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.11.0-1
- Update to 0.11.0

* Mon Oct 02 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.10.1-2
- Rerelease of 0.10.1-1

* Wed Sep 27 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.10.1-1
- Update to 0.10.1
- It improves query performance with name and arch filters. Also nevra filter will now
  handle string with or without epoch.
- Additionally for python bindings it renames NEVRA._has_just_name() to NEVRA.has_just_name() due
  to movement of code into c part of library.
- Resolves: rhbz#1260242 - --exclude does not affect dnf remove's removal of requirements
- Resolves: rhbz#1485881 - DNF claims it cannot install package, which have been already installed
- Resolves: rhbz#1361187 - [abrt] python-ipython-console: filter_updown(): python3.5 killed by SIGABRT

* Fri Sep 15 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.9.3-8
- Disable platform python on old releases

* Tue Aug 15 2017 Lumír Balhar <lbalhar@redhat.com> - 0.9.3-7
- Add platform-python subpackage

* Fri Aug 11 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.9.3-6
- Rebuilt after RPM update (№ 3)

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.9.3-5
- Rebuilt for RPM soname bump

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.9.3-4
- Rebuilt for RPM soname bump

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 24 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.9.3-1
- Update to 0.9.3

* Sat Jul 01 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.9.2-1
- Update to 0.9.2

* Mon Jun 12 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.9.1-1
- Update to 0.9.1

* Mon May 22 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.9.0-1
- Update to 0.9.0

* Tue May 02 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.8.2-1
- Update to 0.8.2

* Fri Mar 24 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.8.1-1
- Update to 0.8.1

* Tue Mar 21 2017 Jaroslav Mracek <jmracek@redhat.com> - 0.8.0-1
- Update to 0.8.0

* Mon Feb 20 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.7.4-1
- Update to 0.7.4

* Fri Feb 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.7.3-1
- Update to 0.7.3

* Wed Feb 08 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.7.2-1
- 0.7.2

* Fri Jan 06 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.7.1-1
- 0.7.1

* Wed Dec 21 2016 Peter Robinson <pbrobinson@fedoraproject.org> 0.7.0-0.7gitf9b798c
- Rebuild for Python 3.6

* Mon Dec 19 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.7.0-0.6gitf9b798c
- Use new upstream URL

* Tue Dec 13 2016 Stratakis Charalampos <cstratak@redhat.com> - 0.7.0-0.5gitf9b798c
- Rebuild for Python 3.6

* Tue Dec 06 2016 Martin Hatina <mhatina@redhat.com> - 0.7.0-0.4gitf9b798c
- Increase conflict version of dnf

* Thu Dec 01 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.7.0-0.3gitf9b798c
- Update to latest snapshot

* Fri Nov 04 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.7.0-0.2git8bd77f8
- Update to latest snapshot

* Thu Sep 29 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.7.0-0.1git179c0a6
- Initial package
