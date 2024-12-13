#
# Conditional build:
%bcond_with	bootstrap	# bootstrap from pre-compiled binaries
%bcond_without	geany		# geany autocompletion support

%define	bootstrap_version 1.27.1
Summary:	LLVM D Compiler
Summary(pl.UTF-8):	Kompilator D oparty na LLVM
Name:		ldc
Version:	1.30.0
Release:	1
# The DMD frontend in dmd/* GPL version 1 or artistic license
# The files gen/asmstmt.cpp and gen/asm-*.hG PL version 2+ or artistic license
License:	BSD
Source0:	https://github.com/ldc-developers/ldc/releases/download/v%{version}/%{name}-%{version}-src.tar.gz
# Source0-md5:	871cec3741a884ff29f564175b919e4d
Source1:	https://github.com/ldc-developers/ldc/releases/download/v%{bootstrap_version}/%{name}2-%{bootstrap_version}-linux-x86_64.tar.xz
# Source1-md5:	1bc671b41ba59848e3d0ffe74c83fc7b
Source3:	macros.%{name}
Patch0:		%{name}-include-path.patch
Patch1:		%{name}-no-default-rpath.patch
URL:		https://github.com/ldc-developers/ldc
BuildRequires:	bash-completion
BuildRequires:	cmake
BuildRequires:	curl-devel
BuildRequires:	gc
%{?with_geany:BuildRequires:	geany}
%{!?with_bootstrap:BuildRequires:	ldc}
BuildRequires:	libconfig-devel
BuildRequires:	libedit-devel
BuildRequires:	libstdc++-devel
BuildRequires:	llvm-devel >= 12
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 2.008
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	zlib-devel
ExclusiveArch:	%{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# Unresolved symbols found: _D4core9exception6_storeG128v (core.exception._store)
%define	skip_post_check_so libphobos2-ldc-debug-shared.so.*

%description
LDC is a portable compiler for the D programming language with modern
optimization and code generation capabilities.

It uses the official DMD compiler frontend to support the latest
version of D, and relies on the LLVM Core libraries for code
generation.

%description -l pl.UTF-8
LDC to przenośny kompilator języka programowania D ze współczesnymi
możliwościami optymalizacji i generowania kodu.

Wykorzystuje frontend oficjalnego kompilatora DMD, aby obsłużyć
najnowszą wersję D i polega na bibliotekach LLVM Core do generowania
kodu.

%package druntime
Summary:	Runtime library for D
Summary(pl.UTF-8):	Biblioteka uruchomieniowa dla D
License:	Boost

%description druntime
Druntime is the minimum library required to support the D programming
language. It includes the system code required to support the garbage
collector, associative arrays, exception handling, array vector
operations, startup/shutdown, etc.

%description druntime -l fr.UTF-8
Druntime est la bibliothèque minimal requise pour supporter la
programmation en D. Est inclut le code système requis pour supporter
le ramasse miette, tableau associatif, gestion des exceptions,
opertation sur des vecteurs, démarage/extinction, etc

%description druntime -l pl.UTF-8
Druntime to minimalna biblioteka wymagana do obsługi języka
programowania D. Zawiera kod systemowy wymagany do obsługi
odśmiecacza, tablice asocjacyjne, obsługę wyjątków, operacje na
wektorach tablic, kod startowy/końcowy itp.

%package phobos
Summary:	D Standard Runtime Library
Summary(pl.UTF-8):	Standardowa biblioteka uruchomieniowa D
License:	Boost
Requires:	%{name}-druntime = %{version}-%{release}

%description phobos
Phobos is the standard library that comes with the D Programming
Language Compiler (<http://dlang.org/>).

%description phobos -l pl.UTF-8
Phobos to biblioteka standardowa dostarczana z kompilatorem języka
programowania D (<http://dlang.org/>).

%package phobos-geany-tags
Summary:	Support for enable autocompletion in geany
Summary(pl.UTF-8):	Obsługa automatycznego dopełniania kodu w geany
Requires:	%{name} = %{version}-%{release}
Requires:	geany
BuildArch:	noarch

%description phobos-geany-tags
Enable autocompletion for Phobos library in geany (IDE).

%description phobos-geany-tags -l fr.UTF-8
Active l'autocompletion pour pour la bibliothèque phobos dans geany
(IDE).

%description phobos-geany-tags -l pl.UTF-8
Obsługa automatycznego dopełniania dla biblioteki Phobos w IDE geany.

%prep
%setup -q -n %{name}-%{version}-src
%patch -P0 -p1
%patch -P1 -p1

%if %{with geany}
# temp geany config directory for allow geany to generate tags
install -d geany_config
%endif

%if %{with bootstrap}
set -- *
install -d build-bootstrap2
cp -al "$@" build-bootstrap2
tar xf %{SOURCE1}
mv ldc2-%{bootstrap_version}-linux-x86_64 build-bootstrap1
%endif

%build
%if %{with bootstrap}
cd build-bootstrap2
%cmake \
	-S .. \
	-B build \
	-DD_COMPILER:PATH=$(pwd)/../build-bootstrap1/bin/ldmd2 \
	-DLDC_WITH_LLD:BOOL=OFF \
	%{nil}
%{__cmake} --build build
cd ..
%endif

%cmake \
	-B build \
	-DMULTILIB:BOOL=OFF \
	-DINCLUDE_INSTALL_DIR:PATH=%{_prefix}/lib/ldc/%{_target_platform}/include/d \
	-DBASH_COMPLETION_COMPLETIONSDIR:PATH=%{_datadir}/bash-completion/completions \
%if %{with bootstrap}
	-DD_COMPILER:PATH=$(pwd)/build-bootstrap2/build/bin/ldmd2 \
%endif
	-DLDC_WITH_LLD:BOOL=OFF \
	%{nil}

%{__cmake} --build build

%if %{with geany}
# generate geany tags
geany -c geany_config -g phobos.d.tags $(find runtime/phobos/std -name "*.d")
%endif

%install
rm -rf $RPM_BUILD_ROOT
DESTDIR="$RPM_BUILD_ROOT" %{__cmake} --install build

# macros for D package
install -d $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d/
install --mode=0644 %{SOURCE3} $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d/macros.ldc

%if %{with geany}
# geany tags
install -d $RPM_BUILD_ROOT%{_datadir}/geany/tags/
cp -p phobos.d.tags $RPM_BUILD_ROOT%{_datadir}/geany/tags/
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md LICENSE
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/ldc2.conf
%attr(755,root,root) %{_bindir}/ldc2
%attr(755,root,root) %{_bindir}/ldmd2
%attr(755,root,root) %{_bindir}/ldc-build-runtime
%attr(755,root,root) %{_bindir}/ldc-profdata
%attr(755,root,root) %{_bindir}/ldc-prune-cache
%{_rpmconfigdir}/macros.d/macros.ldc
%dir %{_prefix}/lib/ldc
%dir %{_prefix}/lib/ldc/%{_target_platform}
%dir %{_prefix}/lib/ldc/%{_target_platform}/include
%dir %{_prefix}/lib/ldc/%{_target_platform}/include/d
%{_prefix}/lib/ldc/%{_target_platform}/include/d/__builtins.di
%{_prefix}/lib/ldc/%{_target_platform}/include/d/core
%{_prefix}/lib/ldc/%{_target_platform}/include/d%{_sysconfdir}
%{_prefix}/lib/ldc/%{_target_platform}/include/d/importc.h
%{_prefix}/lib/ldc/%{_target_platform}/include/d/ldc
%{_prefix}/lib/ldc/%{_target_platform}/include/d/object.d
%{_prefix}/lib/ldc/%{_target_platform}/include/d/std
%{_libdir}/ldc_rt.dso.o
%{_libdir}/libdruntime-ldc-debug-shared.so
%{_libdir}/libdruntime-ldc-shared.so
%{_libdir}/libphobos2-ldc-debug-shared.so
%{_libdir}/libphobos2-ldc-shared.so
%dir %{_datadir}/bash-completion
%dir %{bash_compdir}
%{bash_compdir}/ldc2

%files druntime
%defattr(644,root,root,755)
%doc runtime/druntime/README.md runtime/README runtime/druntime/LICENSE.txt
%{_libdir}/libdruntime-ldc-debug-shared.so.*.*
%ghost %{_libdir}/libdruntime-ldc-debug-shared.so.100
%{_libdir}/libdruntime-ldc-shared.so.*.*
%ghost %{_libdir}/libdruntime-ldc-shared.so.100

%files phobos
%defattr(644,root,root,755)
%doc runtime/phobos/LICENSE_1_0.txt
%{_libdir}/libphobos2-ldc-debug-shared.so.*.*
%ghost %{_libdir}/libphobos2-ldc-debug-shared.so.100
%{_libdir}/libphobos2-ldc-shared.so.*.*
%ghost %{_libdir}/libphobos2-ldc-shared.so.100

%if %{with geany}
%files phobos-geany-tags
%defattr(644,root,root,755)
%{_datadir}/geany/tags/phobos.d.tags
%endif
