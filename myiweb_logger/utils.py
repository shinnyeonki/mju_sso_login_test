"""
로깅 및 공통 유틸리티
====================
콘솔 출력, 로깅, HTTP 요청/응답 로깅 등 공통 기능
"""

import logging
import sys
from typing import Optional


class Colors:
    """터미널 색상 코드"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


class ColoredFormatter(logging.Formatter):
    """색상이 적용된 로그 포맷터"""
    
    LEVEL_COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.RED + Colors.BOLD,
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # 색상 적용
        color = self.LEVEL_COLORS.get(record.levelno, Colors.END)
        
        # 원본 메시지 포맷
        message = super().format(record)
        
        # 레벨에 따라 색상 적용
        return f"{color}{message}{Colors.END}"


def setup_logging(level: int = logging.INFO, use_colors: bool = True) -> None:
    """
    전역 로깅 설정
    
    Args:
        level: 로깅 레벨 (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR)
        use_colors: 색상 출력 여부 (터미널에서 True 권장)
    
    사용 예:
        from myiweb.utils import setup_logging
        import logging
        
        # DEBUG 레벨로 설정 (상세 로그 출력)
        setup_logging(logging.DEBUG)
        
        # INFO 레벨로 설정 (일반 로그만 출력)
        setup_logging(logging.INFO)
        
        # WARNING 이상만 출력
        setup_logging(logging.WARNING)
    """
    # 루트 로거가 아닌 myiweb 패키지 로거 설정
    logger = logging.getLogger('myiweb')
    logger.setLevel(level)
    
    # 기존 핸들러 제거
    logger.handlers.clear()
    
    # 콘솔 핸들러 추가
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # 포맷터 설정
    format_str = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    if use_colors:
        formatter = ColoredFormatter(format_str, datefmt=date_format)
    else:
        formatter = logging.Formatter(format_str, datefmt=date_format)
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # 상위 로거로 전파 방지
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    모듈용 로거 반환
    
    Args:
        name: 모듈 이름 (보통 __name__ 사용)
    
    Returns:
        logging.Logger: 설정된 로거
    
    사용 예:
        from myiweb.utils import get_logger
        logger = get_logger(__name__)
        
        logger.debug("디버그 메시지")
        logger.info("정보 메시지")
        logger.warning("경고 메시지")
        logger.error("에러 메시지")
    """
    return logging.getLogger(name)


# 기존 호환성을 위한 함수들 (logging 기반으로 재구현)
_compat_logger = logging.getLogger('myiweb.compat')


def log_section(title: str) -> None:
    """섹션 구분선 출력"""
    _compat_logger.info(f"\n{'='*70}\n {title}\n{'='*70}\n")


def log_step(step_num: str, title: str) -> None:
    """단계 출력"""
    _compat_logger.info(f"[Step {step_num}] {title}")


def log_info(label: str, value, indent: int = 2) -> None:
    """정보 출력"""
    spaces = ' ' * indent
    if isinstance(value, dict):
        lines = [f"{spaces}{label}:"]
        for k, v in value.items():
            # 민감 정보 마스킹
            if 'password' in k.lower() or 'pw' in k.lower():
                v = '****' if v else '(empty)'
            lines.append(f"{spaces}  {k}: {v}")
        _compat_logger.debug('\n'.join(lines))
    elif isinstance(value, str) and len(value) > 100:
        _compat_logger.debug(f"{spaces}{label}: {value[:50]}...({len(value)} chars)")
    else:
        _compat_logger.debug(f"{spaces}{label}: {value}")


def log_success(message: str) -> None:
    """성공 메시지"""
    _compat_logger.info(f"✓ {message}")


def log_error(message: str) -> None:
    """에러 메시지"""
    _compat_logger.error(f"✗ {message}")


def log_warning(message: str) -> None:
    """경고 메시지"""
    _compat_logger.warning(f"⚠ {message}")


def log_request(method: str, url: str, headers: dict = None, data: dict = None) -> None:
    """HTTP 요청 로깅"""
    lines = [f"\n>>> {method} Request >>>", f"  URL: {url}"]
    if headers:
        important_headers = {k: v for k, v in headers.items() 
                          if k.lower() in ['content-type', 'origin', 'referer', 'cookie']}
        if important_headers:
            lines.append(f"  Headers: {important_headers}")
    if data:
        safe_data = {k: ('****' if 'pw' in k.lower() and v else v) for k, v in data.items()}
        lines.append(f"  Form Data: {safe_data}")
    _compat_logger.debug('\n'.join(lines))


def log_response(response, show_body: bool = False, max_body_length: int = 2000) -> None:
    """HTTP 응답 로깅"""
    lines = [
        f"\n<<< Response <<<",
        f"  Status Code: {response.status_code}",
        f"  Final URL: {response.url}"
    ]
    
    # 주요 응답 헤더만 출력
    important_headers = ['Content-Type', 'Location', 'Set-Cookie']
    for header_name in important_headers:
        if header_name in response.headers:
            lines.append(f"    {header_name}: {response.headers[header_name]}")
    
    # 쿠키 출력
    if response.cookies:
        lines.append(f"  [Response Cookies]: {dict(response.cookies)}")
    
    # 응답 본문 출력 (옵션)
    if show_body:
        body = response.text
        if len(body) > max_body_length:
            lines.append(f"  [Response Body] (총 {len(body)} chars, 처음 {max_body_length}자만 표시)")
            lines.append(f"    {'-'*60}")
            lines.append(body[:max_body_length])
            lines.append(f"    ... (생략됨)")
        else:
            lines.append(f"  [Response Body]")
            lines.append(f"    {'-'*60}")
            lines.append(body)
        lines.append(f"    {'-'*60}")
    
    _compat_logger.debug('\n'.join(lines))


def mask_sensitive(text: str, visible_chars: int = 4) -> str:
    """민감한 정보 마스킹"""
    if not text or len(text) <= visible_chars:
        return '****'
    return f"{text[:visible_chars]}****"
