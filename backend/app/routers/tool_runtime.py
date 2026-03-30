from fastapi import APIRouter, Depends

from ..deps import state, get_redis, get_search_svc, get_embed_model, get_code_tools
from ..envelopes import ok
from ..envelopes import ApiError
from ..schemas.tool_api import (
    CheckAccessRequest,
    CiteBundleRequest,
    CollectEvidenceRequest,
    GetDocMetadataRequest,
    ListRepoFilesRequest,
    OpenDocChunksRequest,
    ReadCodeRequest,
    RunBuildRequest,
    SearchCodeRequest,
    SearchDocsRequest,
    SvnDiffRequest,
    SvnRepoRequest,
    SvnStatusRequest,
    SubmitFeedbackRequest,
    UserContextRequest,
)
from ..core.document_store import DocumentStoreService
from ..services.tools.support import normalize_citation_items, submit_feedback
from ..services.tools.runtime import (
    collect_evidence_bundle,
    get_doc_metadata,
    list_repo_files,
    open_doc_chunks,
    read_code_lines,
    run_build,
    search_code,
    search_docs,
    svn_diff,
    svn_info,
    svn_status,
)
from ..services.tools.access import (
    check_code_path_access,
    resolve_tool_user_context,
)


router = APIRouter(prefix="/tool-api")


@router.post("/user/acl/get_user_context")
async def get_user_context(request: UserContextRequest, redis=Depends(get_redis)):
    policy_context = await resolve_tool_user_context(
        redis, session_id=request.session_id, user_id=request.user_id
    )
    return ok(
        {
            "user_id": request.user_id or "anonymous",
            "email": request.email or "anonymous@local",
            "groups": request.groups or ["public"],
            "roles": request.roles or ["agent"],
            "org_path": request.org_path or ["local"],
            "workspace": request.workspace,
            "session_id": request.session_id,
            "policy_context": policy_context,
        }
    )


@router.post("/user/acl/check_access")
async def check_access(request: CheckAccessRequest):
    requested_ids = [rid for rid in request.resource_ids if str(rid).strip()]
    if request.resource_id and request.resource_id not in requested_ids:
        requested_ids.append(request.resource_id)

    decisions = {rid: True for rid in requested_ids}

    return ok(
        {
            "user_id": request.user_id or "anonymous",
            "action": request.action,
            "resource": request.resource,
            "resource_ids": requested_ids,
            "resource_id": request.resource_id,
            "allow": True,
            "decisions": decisions,
            "reason": "allow",
            "policy_version": "v1",
        }
    )


@router.post("/docs/search_docs")
async def docs_search(
    request: SearchDocsRequest,
    redis=Depends(get_redis),
    search_svc=Depends(get_search_svc),
    embed_model=Depends(get_embed_model),
):
    result = await search_docs(
        redis,
        search_svc,
        embed_model,
        request.query,
        request.filters,
        request.top_k,
        session_id=request.session_id,
        use_reranker=request.use_reranker,
    )
    if result.get("reason") == "context_required":
        raise ApiError("TOOL_POLICY_VIOLATION", "context_required", status_code=400)
    return ok(result)


@router.post("/docs/open_doc_chunks")
async def docs_open_chunks(
    request: OpenDocChunksRequest,
    redis=Depends(get_redis),
    search_svc=Depends(get_search_svc),
):
    result = await open_doc_chunks(
        redis,
        search_svc,
        request.chunk_ids,
        request.max_chars,
        session_id=request.session_id,
        explicit_reference=False,
    )
    if result.get("reason") in {"context_required", "search_required", "unknown_chunk_ids"}:
        raise ApiError("TOOL_POLICY_VIOLATION", result.get("reason", "tool_policy_violation"), status_code=400)
    return ok(result)
@router.post("/docs/get_doc_metadata")
async def docs_metadata(request: GetDocMetadataRequest, redis=Depends(get_redis)):
    doc_store = DocumentStoreService(redis)
    result = await get_doc_metadata(doc_store, request.doc_id)
    return ok(result)


@router.post("/code/list_repo_files")
async def code_list_files(
    request: ListRepoFilesRequest,
    redis=Depends(get_redis),
    code_tools=Depends(get_code_tools),
):
    result = await list_repo_files(
        redis, code_tools, request.glob, request.limit, request.session_id
    )
    if result.get("reason") == "context_required":
        raise ApiError("TOOL_POLICY_VIOLATION", "context_required", status_code=400)
    return ok(result)


@router.post("/code/svn_info")
async def code_svn_info(
    request: SvnRepoRequest,
    redis=Depends(get_redis),
    code_tools=Depends(get_code_tools),
):
    result = await svn_info(redis, code_tools, request.workspace_path, request.session_id)
    if result.get("reason") == "context_required":
        raise ApiError("TOOL_POLICY_VIOLATION", "context_required", status_code=400)
    return ok(result)


@router.post("/code/svn_status")
async def code_svn_status(
    request: SvnStatusRequest,
    redis=Depends(get_redis),
    code_tools=Depends(get_code_tools),
):
    result = await svn_status(
        redis,
        code_tools,
        request.workspace_path,
        request.path_filter,
        request.limit,
        request.session_id,
    )
    if result.get("reason") == "context_required":
        raise ApiError("TOOL_POLICY_VIOLATION", "context_required", status_code=400)
    return ok(result)


@router.post("/code/svn_diff")
async def code_svn_diff(
    request: SvnDiffRequest,
    redis=Depends(get_redis),
    code_tools=Depends(get_code_tools),
):
    result = await svn_diff(
        redis,
        code_tools,
        request.workspace_path,
        request.path_filter,
        request.max_chars,
        request.session_id,
    )
    if result.get("reason") == "context_required":
        raise ApiError("TOOL_POLICY_VIOLATION", "context_required", status_code=400)
    return ok(result)


@router.post("/code/search_code")
async def code_search(
    request: SearchCodeRequest,
    redis=Depends(get_redis),
    code_tools=Depends(get_code_tools),
):
    result = await search_code(
        redis,
        code_tools,
        request.query_or_regex,
        request.path_filter,
        request.limit,
        request.session_id,
    )
    if result.get("reason") == "context_required":
        raise ApiError("TOOL_POLICY_VIOLATION", "context_required", status_code=400)
    return ok(result)


@router.post("/code/read_code")
async def code_read(
    request: ReadCodeRequest,
    redis=Depends(get_redis),
    code_tools=Depends(get_code_tools),
):
    access = await check_code_path_access(redis, request.session_id, request.path, explicit_reference=False)
    if not access["allow"]:
        raise ApiError("TOOL_POLICY_VIOLATION", access.get("reason", "tool_policy_violation"), status_code=400)

    result = read_code_lines(code_tools, request.path, request.start_line, request.end_line)
    return ok(result)


@router.post("/code/run_build")
async def code_run_build(
    request: RunBuildRequest,
    redis=Depends(get_redis),
    code_tools=Depends(get_code_tools),
):
    result = await run_build(
        redis,
        code_tools,
        workspace_path=request.workspace_path,
        tool=request.tool,
        project_or_solution=request.project_or_solution,
        target=request.target,
        configuration=request.configuration,
        args=request.args,
        timeout_sec=request.timeout_sec,
        max_chars=request.max_chars,
        session_id=request.session_id,
    )
    if result.get("reason") == "context_required":
        raise ApiError("TOOL_POLICY_VIOLATION", "context_required", status_code=400)
    if result.get("reason") == "workspace_not_found":
        raise ApiError("WORKSPACE_NOT_FOUND", "workspace_not_found", status_code=404)
    if result.get("reason") == "invalid_request":
        raise ApiError("INVALID_BUILD_REQUEST", result.get("message", "invalid_request"), status_code=400)
    return ok(result)


@router.post("/orchestrate/collect_evidence")
async def orchestrate_collect_evidence(
    request: CollectEvidenceRequest,
    redis=Depends(get_redis),
    search_svc=Depends(get_search_svc),
    embed_model=Depends(get_embed_model),
    code_tools=Depends(get_code_tools),
):
    doc_store = DocumentStoreService(redis)
    result = await collect_evidence_bundle(
        redis,
        search_svc,
        embed_model,
        code_tools,
        doc_store=doc_store,
        session_id=request.session_id,
        user_id=request.user_id,
        query=request.query,
        filters=request.filters,
        mode=request.mode,
        response_type=request.response_type,
        top_k=request.top_k,
        limit=request.limit,
        max_chars=request.max_chars,
        max_line_span=request.max_line_span,
    )
    return ok(result)


@router.post("/quality/cite_bundle")
async def quality_cite_bundle(request: CiteBundleRequest):
    normalized = normalize_citation_items([item.dict() for item in request.items])
    return ok(
        {
            "items": normalized,
            "count": len(normalized),
        }
    )


@router.post("/quality/submit_feedback")
async def quality_submit_feedback(request: SubmitFeedbackRequest, redis=Depends(get_redis)):
    result = await submit_feedback(redis, request.question, request.answer, request.rating, request.tags)
    return ok(result)
