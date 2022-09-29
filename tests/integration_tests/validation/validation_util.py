"""A helper to extract test data results."""

from __future__ import annotations

import os.path
import pathlib
from collections import Counter
from pathlib import PurePosixPath
import warnings
import pytest
from _pytest.mark.structures import ParameterSet

from arelle import ModelDocument, PackageManager, PluginManager
from arelle.CntlrCmdLine import parseAndRun


def get_test_data(
    args: list[str],
    expected_failure_ids: frozenset[str] = frozenset(),
    expected_empty_testcases: frozenset[str] = frozenset(),
) -> list[ParameterSet]:
    """
    Produces a list of Pytest Params that can be fed into a parameterized pytest function

    :param args: The args to be parsed by arelle in order to correctly produce the desired result set
    :param expected_failure_ids: The set of string test IDs that are expected to fail
    :param expected_empty_testcases: The set of paths of empty testcases, relative to the suite zip
    """
    cntlr = parseAndRun(args)
    try:
        results: list[ParameterSet] = []
        test_cases_with_no_variations = set()
        test_cases_with_unrecognized_type = {}
        model_document = cntlr.modelManager.modelXbrl.modelDocument
        test_cases: list[ModelDocument.ModelDocument] = []
        if model_document.type in (
            ModelDocument.Type.TESTCASE,
            ModelDocument.Type.REGISTRYTESTCASE,
        ):
            test_cases.append(model_document)
        elif model_document.type == ModelDocument.Type.TESTCASESINDEX:
            referenced_documents = model_document.referencesDocument.keys()
            child_document_types = {doc.type for doc in referenced_documents}
            assert (
                len(child_document_types) == 1
            ), f"Multiple child document types found in {model_document.uri}: {child_document_types}."
            [child_document_type] = child_document_types
            # the formula function registry conformance suite points to a list of registries, so we need to search one level deeper.
            if child_document_type == ModelDocument.Type.REGISTRY:
                referenced_documents = [
                    case
                    for doc in referenced_documents
                    for case in doc.referencesDocument.keys()
                ]
            test_cases = sorted(referenced_documents, key=lambda doc: doc.uri)
        else:
            raise Exception(f"Unhandled model document type: {model_document.type}")
        for test_case in test_cases:
            file_extension = pathlib.Path(test_case.uri).suffix
            if test_case.type not in (
                ModelDocument.Type.TESTCASE,
                ModelDocument.Type.REGISTRYTESTCASE,
            ):
                test_cases_with_unrecognized_type[file_extension] = test_case.type
            if (
                not getattr(test_case, "testcaseVariations", None)
                and os.path.relpath(
                    test_case.filepath, model_document.modelXbrl.fileSource.basefile
                )
                not in expected_empty_testcases
            ):
                test_cases_with_no_variations.add(file_extension)
            else:
                for mv in test_case.testcaseVariations:
                    test_id = "{}/{}".format("/".join(file_extension), mv.id)
                    param = pytest.param(
                        {
                            'status': mv.status,
                            'expected': mv.expected,
                            'actual': mv.actual,
                        },
                        id=test_id,
                        marks=[pytest.mark.xfail()]
                        if test_id in expected_failure_ids
                        else [],
                    )
                    results.append(param)
        if test_cases_with_unrecognized_type:
            raise Exception(
                f"Some test cases have an unrecognized document type: {sorted(test_cases_with_unrecognized_type.items())}."
            )
        if test_cases_with_no_variations:
            warnings.warn(
                f"Some test cases don't have any variations: {sorted(test_cases_with_no_variations)}."
            )
        test_id_frequencies = Counter(p.id for p in results)
        nonunique_test_ids = {
            test_id: count
            for test_id, count in test_id_frequencies.items()
            if count > 1
        }
        if nonunique_test_ids:
            warnings.warn(
                f"Some test IDs are not unique. Frequencies of nonunique test IDs: {nonunique_test_ids}."
            )
        nonexistent_expected_failure_ids = expected_failure_ids - set(
            test_id_frequencies
        )
        if nonexistent_expected_failure_ids:
            warnings.warn(
                f"Some expected failure IDs don't match any test cases: {sorted(nonexistent_expected_failure_ids)}."
            )
        return results
    finally:
        cntlr.modelManager.close()
        PackageManager.close()
        PluginManager.close()
