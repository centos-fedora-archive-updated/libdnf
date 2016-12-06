%global commit f9b798cadb6821f9cffd5c0331578b3f7c19d699
%global shortcommit %(c=%{commit}; echo ${c:0:7})

%global libsolv_version 0.6.21-1
%global dnf_conflict 2.0.0-0.rc2.4

%bcond_with valgrind

# Do not build bindings for python3 for RHEL <= 7
%if 0%{?rhel} && 0%{?rhel} <= 7
%bcond_with python3
%else
%bcond_without python3
%endif

%global oldname libhif

Name:           libdnf
Version:        0.7.0
Release:        0.4git%{shortcommit}%{?dist}
Summary:        Library providing simplified C and Python API to libsolv
License:        LGPLv2+
URL:            https://github.com/rpm-software-management/%{oldname}
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  libsolv-devel >= %{libsolv_version}
BuildRequires:  pkgconfig(librepo)
BuildRequires:  pkgconfig(check)
%if %{with valgrind}
BuildRequires:  valgrind
%endif
BuildRequires:  pkgconfig(gio-unix-2.0) >= 2.44.0
BuildRequires:  pkgconfig(gtk-doc)
BuildRequires:  pkgconfig(gobject-introspection-1.0)
BuildRequires:  rpm-devel >= 4.11.0

Requires:       libsolv%{?_isa} >= %{libsolv_version}

%description
A Library providing simplified C and Python API to libsolv.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libsolv-devel%{?_isa} >= %{libsolv_version}
BuildRequires:  python-nose

%description devel
Development files for %{name}.

%package -n python2-hawkey
Summary:        Python 2 bindings for the hawkey library
%{?python_provide:%python_provide python2-hawkey}
BuildRequires:  python2-devel
BuildRequires:  python-nose
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
%{?system_python_abi}
%{?python_provide:%python_provide python3-hawkey}
BuildRequires:  python3-devel
BuildRequires:  python3-nose
Requires:       %{name}%{?_isa} = %{version}-%{release}
# Fix problem with hawkey - dnf version incompatibility
# Can be deleted for distros where only python3-dnf >= 2.0.0
Conflicts:      python3-dnf < %{dnf_conflict}

%description -n python3-hawkey
Python 3 bindings for the hawkey library.
%endif

%prep
%autosetup -n %{oldname}-%{commit}
mkdir build-py2
%if %{with python3}
mkdir build-py3
%endif

%build
pushd build-py2
  %cmake -DWITH_MAN=OFF ../ %{!?with_valgrind:-DDISABLE_VALGRIND=1}
  %make_build
popd

%if %{with python3}
pushd build-py3
  %cmake -DPYTHON_DESIRED:str=3 -DWITH_GIR=0 -DWITH_MAN=0 -Dgtkdoc=0 ../ %{!?with_valgrind:-DDISABLE_VALGRIND=1}
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

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

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
* Tue Dec 06 2016 Martin Hatina <mhatina@redhat.com> - 0.7.0-0.4gitf9b798c
- Increase conflict version of dnf

* Thu Dec 01 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 0.7.0-0.3gitf9b798c
- Update to latest snapshot

* Fri Nov 04 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.7.0-0.2git8bd77f8
- Update to latest snapshot

* Thu Sep 29 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.7.0-0.1git179c0a6
- Initial package
