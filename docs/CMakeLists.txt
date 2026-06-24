
cmake_minimum_required(VERSION 3.25)

# Get version from python package
file(READ "${CMAKE_CURRENT_SOURCE_DIR}/../src/peakrdl_halcpp/__about__.py" _about)
string(REGEX MATCH "__version__ = \"([^\"]+)\"" _ ${_about})
set(_halcpp_version ${CMAKE_MATCH_1})

project(PeakRDL-halcpp-Documentation
        VERSION ${_halcpp_version}
)

find_package(Python3 COMPONENTS Interpreter REQUIRED)
set(Python3_EXECUTABLE "${Python3_EXECUTABLE}" CACHE FILEPATH "Path to Python3 interpreter")

include(FindPackageHandleStandardArgs)

# -----------------------------------------------------------------------
# Sphinx HTML target (kept for reference / standalone use)
# -----------------------------------------------------------------------
find_program(
    SPHINX_APIDOC
    NAMES sphinx-apidoc
    HINTS ${Python3_VIRTUAL_ENV}/bin
    REQUIRED
)
find_package_handle_standard_args(Sphinx-apidoc DEFAULT_MSG SPHINX_APIDOC)

set(API_DOC_INPUT_DIR "${PROJECT_SOURCE_DIR}/../src/")
set(API_SPHINX_SRC_DIR "${PROJECT_BINARY_DIR}/api/sphinx_docs/")
set(API_SPHINX_BUILD_DIR "${API_SPHINX_SRC_DIR}/_build/")
set(SPHINX_TMPL_DIR "${API_SPHINX_SRC_DIR}/_templates/")

# Template files configured at cmake-configure time.
configure_file(${PROJECT_SOURCE_DIR}/sphinx_config/conf.py.jinja ${SPHINX_TMPL_DIR}/conf.py.jinja @ONLY)
configure_file(${PROJECT_SOURCE_DIR}/sphinx_config/master_doc.rst.jinja ${SPHINX_TMPL_DIR}/master_doc.rst.jinja COPYONLY)
configure_file(${PROJECT_SOURCE_DIR}/sphinx_config/Makefile.in ${API_SPHINX_SRC_DIR}/Makefile @ONLY)

# Step 1: sphinx-apidoc --full generates RST stubs and runs sphinx-quickstart,
#         which renders conf.py from conf.py.jinja and produces index.rst.
#         conf.py is removed first so quickstart always re-applies the template.
set(SPHINX_APIDOC_STAMP "${PROJECT_BINARY_DIR}/sphinx_apidoc.stamp")
set(SPHINX_CONF_PY "${API_SPHINX_SRC_DIR}/conf.py")

set(API_DOC_RST_CMD
    ${SPHINX_APIDOC} --full --module-first -a
    -H "PeakRDL-halcpp API" -A CERN -V ${PROJECT_VERSION} -R ${PROJECT_VERSION}
    --templatedir=${SPHINX_TMPL_DIR}
    -o ${API_SPHINX_SRC_DIR} ${API_DOC_INPUT_DIR}
)

add_custom_command(
        OUTPUT ${SPHINX_APIDOC_STAMP} ${SPHINX_CONF_PY}
        COMMAND "${CMAKE_COMMAND}" -E make_directory "${API_SPHINX_SRC_DIR}"
        COMMAND "${CMAKE_COMMAND}" -E rm -f "${SPHINX_CONF_PY}"
        COMMAND ${API_DOC_RST_CMD}
        COMMAND "${CMAKE_COMMAND}" -E touch ${SPHINX_APIDOC_STAMP}
        DEPENDS
            ${SPHINX_TMPL_DIR}/conf.py.jinja
            ${SPHINX_TMPL_DIR}/master_doc.rst.jinja
        COMMENT "Generating PeakRDL-halcpp Sphinx RST files."
)

# Step 2: Build Sphinx HTML from the generated project.
set(API_DOC_HTML_CMD make -C ${API_SPHINX_SRC_DIR} html)
set(API_INDEX_HTML_FILE "${API_SPHINX_BUILD_DIR}/html/index.html")

add_custom_command(
        OUTPUT ${API_INDEX_HTML_FILE}
        COMMAND ${API_DOC_HTML_CMD}
        DEPENDS ${SPHINX_APIDOC_STAMP} ${SPHINX_CONF_PY}
        COMMENT "Building Sphinx HTML documentation."
)

add_custom_target(api_doc DEPENDS ${API_INDEX_HTML_FILE})
set_target_properties(api_doc PROPERTIES
        ADDITIONAL_CLEAN_FILES "${SPHINX_APIDOC_STAMP};${API_SPHINX_SRC_DIR}"
)

# Copy Sphinx HTML into Docusaurus static folder so it is served as a
# static asset at /api_sphinx/index.html
set(SPHINX_STATIC_DIR "${PROJECT_SOURCE_DIR}/static/api_sphinx")
set(SPHINX_STATIC_STAMP "${PROJECT_BINARY_DIR}/sphinx_static.stamp")

add_custom_command(
        OUTPUT ${SPHINX_STATIC_STAMP}
        COMMAND ${CMAKE_COMMAND} -E copy_directory "${API_SPHINX_BUILD_DIR}/html" "${SPHINX_STATIC_DIR}"
        COMMAND ${CMAKE_COMMAND} -E touch ${SPHINX_STATIC_STAMP}
        DEPENDS ${API_INDEX_HTML_FILE}
        COMMENT "Copying Sphinx HTML to Docusaurus static folder."
)

add_custom_target(copy_sphinx_static DEPENDS ${SPHINX_STATIC_STAMP})
set_target_properties(copy_sphinx_static PROPERTIES
        ADDITIONAL_CLEAN_FILES "${SPHINX_STATIC_DIR}"
)

# -----------------------------------------------------------------------
# Docusaurus build and dev server
# Both targets depend on copy_sphinx_static so that running either
# make target drives the full documentation pipeline.
# -----------------------------------------------------------------------
find_program(NPM_EXECUTABLE npm REQUIRED)
find_package_handle_standard_args(npm DEFAULT_MSG NPM_EXECUTABLE)

set(DOCUSAURUS_OUT_DIR ${PROJECT_BINARY_DIR}/docusaurus)
file(MAKE_DIRECTORY ${DOCUSAURUS_OUT_DIR})
set(DOCUSAURUS_STAMP_FILE ${DOCUSAURUS_OUT_DIR}/stamp.stamp)

add_custom_command(
        OUTPUT ${DOCUSAURUS_STAMP_FILE}
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
        COMMAND ${CMAKE_COMMAND} -E touch ${DOCUSAURUS_STAMP_FILE}
        COMMAND ${NPM_EXECUTABLE} install
        COMMAND ${NPM_EXECUTABLE} run build -- --out-dir ${DOCUSAURUS_OUT_DIR}
        DEPENDS ${SPHINX_STATIC_STAMP}
        COMMENT "Building Docusaurus documentation."
)

add_custom_target(docusaurus_doc
        DEPENDS ${DOCUSAURUS_STAMP_FILE}
        COMMENT "Building Docusaurus documentation."
)

add_custom_target(docusaurus_start
        DEPENDS copy_sphinx_static
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
        COMMAND ${NPM_EXECUTABLE} install
        COMMAND ${NPM_EXECUTABLE} run start
        COMMENT "Starting Docusaurus dev server."
)
