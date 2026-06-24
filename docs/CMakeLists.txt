
cmake_minimum_required(VERSION 3.25)

project(PeakRDL-halcpp-Documentation
        VERSION 0.4.2
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

set(API_DOC_RST_CMD ${SPHINX_APIDOC} --full --module-first -a -H ${PROJECT_NAME} -A CERN -R ${PROJECT_VERSION} --templatedir=${SPHINX_TMPL_DIR} -o ${API_SPHINX_SRC_DIR} ${API_DOC_INPUT_DIR})
set(API_DOC_HTML_CMD make -C ${API_SPHINX_SRC_DIR} html)
set(API_INDEX_HTML_FILE "${API_SPHINX_BUILD_DIR}/html/index.html")

add_custom_command(
        OUTPUT ${API_SPHINX_SRC_DIR}
        COMMAND "${CMAKE_COMMAND}" -E make_directory "${API_SPHINX_SRC_DIR}"
        COMMENT "Create Sphinx output directory."
)

add_custom_command(
        OUTPUT ${API_INDEX_HTML_FILE}
        COMMAND ${API_DOC_RST_CMD}
        COMMAND ${API_DOC_HTML_CMD}
        DEPENDS ${API_SPHINX_SRC_DIR}
        COMMENT "Generating PeakRDL-halcpp Sphinx HTML documentation."
)

add_custom_target(api_doc DEPENDS ${API_INDEX_HTML_FILE})

configure_file(${PROJECT_SOURCE_DIR}/sphinx_config/conf.py.in ${SPHINX_TMPL_DIR}/conf.py_t @ONLY)
configure_file(${PROJECT_SOURCE_DIR}/sphinx_config/Makefile.in ${SPHINX_TMPL_DIR}/Makefile_t @ONLY)
configure_file(${PROJECT_SOURCE_DIR}/sphinx_config/master_doc.rst.jinja ${SPHINX_TMPL_DIR}/master_doc.rst.jinja COPYONLY)
configure_file(${PROJECT_SOURCE_DIR}/sphinx_config/Makefile.in ${API_SPHINX_SRC_DIR}/Makefile @ONLY)

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
# pydoc-markdown → Docusaurus-native Markdown (docs/docs/api/)
# -----------------------------------------------------------------------
find_program(
    PYDOC_MARKDOWN_EXECUTABLE
    NAMES pydoc-markdown
    HINTS ${Python3_VIRTUAL_ENV}/bin
    REQUIRED
)
find_package_handle_standard_args(pydoc-markdown DEFAULT_MSG PYDOC_MARKDOWN_EXECUTABLE)

set(API_MD_STAMP "${PROJECT_BINARY_DIR}/api_md.stamp")

add_custom_command(
        OUTPUT ${API_MD_STAMP}
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
        COMMAND ${PYDOC_MARKDOWN_EXECUTABLE}
        COMMAND ${CMAKE_COMMAND} -E touch ${API_MD_STAMP}
        COMMENT "Generating Python API Markdown with pydoc-markdown."
)

set(API_MD_OUTPUT_DIR "${PROJECT_SOURCE_DIR}/docs/api")
add_custom_target(api_doc_md DEPENDS ${API_MD_STAMP})
set_target_properties(api_doc_md PROPERTIES
        ADDITIONAL_CLEAN_FILES "${API_MD_OUTPUT_DIR}"
)

# -----------------------------------------------------------------------
# Docusaurus build and dev server
# Both targets depend on api_doc_md and copy_sphinx_static so that
# running either make target drives the full documentation pipeline.
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
        DEPENDS ${API_MD_STAMP} ${SPHINX_STATIC_STAMP}
        COMMENT "Building Docusaurus documentation."
)

add_custom_target(docusaurus_doc
        DEPENDS ${DOCUSAURUS_STAMP_FILE}
        COMMENT "Building Docusaurus documentation."
)

add_custom_target(docusaurus_start
        DEPENDS api_doc_md copy_sphinx_static
        WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
        COMMAND ${NPM_EXECUTABLE} install
        COMMAND ${NPM_EXECUTABLE} run start
        COMMENT "Starting Docusaurus dev server."
)
