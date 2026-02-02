"""
文档管理API端点
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import List
import os
import shutil
from pathlib import Path
from datetime import datetime
import uuid

router = APIRouter()

# 支持的文件类型
ALLOWED_EXTENSIONS = {
    '.pdf', '.txt', '.csv', '.xlsx', '.xls', '.md', '.ppt', '.pptx', '.docx', '.doc'
}

# 文件类型映射
FILE_TYPE_MAPPING = {
    '.pdf': 'pdf',
    '.txt': 'text',
    '.csv': 'csv',
    '.xlsx': 'excel',
    '.xls': 'excel',
    '.md': 'markdown',
    '.ppt': 'powerpoint',
    '.pptx': 'powerpoint',
    '.docx': 'word',
    '.doc': 'word',
}


def get_document_dir():
    """获取文档存储目录"""
    from app.core.config import settings
    doc_path = Path(settings.DOC_PATH)
    doc_path.mkdir(parents=True, exist_ok=True)
    return doc_path


def validate_file(filename: str) -> bool:
    """验证文件类型是否允许"""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    上传文档到本地知识库

    支持的格式: PDF, TXT, CSV, XLSX, MD, PPT, PPTX, DOCX, DOC
    """
    try:
        # 验证文件类型
        if not validate_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型。支持的类型: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # 读取文件内容
        content = await file.read()

        # 生成唯一文件名
        file_ext = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # 保存文件
        doc_dir = get_document_dir()
        file_path = doc_dir / unique_filename

        with open(file_path, "wb") as f:
            f.write(content)

        # 获取文件大小
        file_size = len(content)

        # 返回文档信息
        document_info = {
            "id": unique_filename.split('.')[0],  # 使用UUID作为ID
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_type": FILE_TYPE_MAPPING.get(file_ext, 'unknown'),
            "file_size": file_size,
            "uploaded_at": datetime.utcnow().isoformat(),
            "file_path": str(file_path)
        }

        return document_info

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )


@router.get("/")
async def list_documents():
    """
    列出所有已上传的文档
    """
    try:
        doc_dir = get_document_dir()
        documents = []

        if not doc_dir.exists():
            return []

        # 遍历文档目录
        for file_path in doc_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                stat = file_path.stat()
                file_id = file_path.stem  # UUID作为ID

                documents.append({
                    "id": file_id,
                    "filename": file_path.name,
                    "file_type": FILE_TYPE_MAPPING.get(file_path.suffix.lower(), 'unknown'),
                    "file_size": stat.st_size,
                    "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "file_path": str(file_path)
                })

        # 按上传时间倒序排列
        documents.sort(key=lambda x: x["uploaded_at"], reverse=True)

        return documents

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取文档列表失败: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    删除指定文档
    """
    try:
        doc_dir = get_document_dir()

        # 查找文件（尝试各种扩展名）
        found = False
        for ext in ALLOWED_EXTENSIONS:
            file_path = doc_dir / f"{document_id}{ext}"
            if file_path.exists():
                file_path.unlink()
                found = True
                break

        if not found:
            raise HTTPException(
                status_code=404,
                detail=f"文档不存在: {document_id}"
            )

        return {"message": "文档删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除文档失败: {str(e)}"
        )


@router.get("/{document_id}/download")
async def download_document(document_id: str):
    """
    下载指定文档
    """
    try:
        doc_dir = get_document_dir()

        # 查找文件
        file_path = None
        original_filename = None

        for ext in ALLOWED_EXTENSIONS:
            potential_path = doc_dir / f"{document_id}{ext}"
            if potential_path.exists():
                file_path = potential_path
                # 尝试从元数据中获取原始文件名
                original_filename = f"document_{document_id}{ext}"
                break

        if not file_path:
            raise HTTPException(
                status_code=404,
                detail=f"文档不存在: {document_id}"
            )

        return FileResponse(
            path=str(file_path),
            filename=original_filename,
            media_type='application/octet-stream'
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"下载文档失败: {str(e)}"
        )
