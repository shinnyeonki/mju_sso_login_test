/**
 * SweetAlert2 Custom 다이얼로그 통합본 (오버로딩)
 * 
 * @param title			alert 의 제목
 * @param text			alert 의 content 값
 * @param func			alert 이후 동작함수 (setTimeout 이 500ms 로 되어있으므로 0.5초 이후 실행)
 * 						ex) () => { console.log('test'); }
 * @returns void
 */ 
function createSweetAlert2Dialog(title, text, func) {
	createSweetAlert2Dialog(title, text, func, null);
}

/**
 * SweetAlert2 Custom 다이얼로그 통합본
 * 
 * @param title			alert 의 제목
 * @param text			alert 의 content 값
 * @param func			alert 이후 동작함수 (setTimeout 이 500ms 로 되어있으므로 0.5초 이후 실행)
 * 						ex) () => { console.log('test'); }
 * @param iconName		icon 타입 ['success', 'error', 'warning', 'info', 'question']
 * @returns void
 */ 
function createSweetAlert2Dialog(title, text, func, iconName) {
	if(iconName == null || iconName == undefined || iconName.trim() == '') {
		createSweetAlert2Warning(title, text, func);
	} else {
		switch(iconName.trim()) {
			case 'success':
				createSweetAlert2Success(title, text, func);
				break;
			case 'error':
				createSweetAlert2Warning(title, text, func);
				break;
			case 'warning':
				createSweetAlert2Warning2(title, text, func);
				break;
			case 'info':
				createSweetAlert2Info(title, text, func);
				break;
			case 'question':
				createSweetAlert2Question(title, text, func);
				break;
			default:
				createSweetAlert2Warning(title, text, func);
		}
	}
}


// SweetAlert2 Custom error method (Legacy)
// ex) createSweetAlert2Warning('테스트', '테스트 입니다.', () => { console.log('test'); });
function createSweetAlert2Warning (title, text, func) {
	try {
		Swal.fire({
			icon: 'error',
			title: title,
			html: text
		}).then((result) => {
			setTimeout(() => {func()}, 500);
		});	
	} catch(e) {
		alert(text);
		func();
	}
}

//SweetAlert2 Custom Warning method (Legacy)
//ex) createSweetAlert2Warning2('테스트', '테스트 입니다.', () => { console.log('test'); });
function createSweetAlert2Warning2 (title, text, func) {
	try {
		Swal.fire({
			icon: 'warning',
			title: title,
			html: text
		}).then((result) => {
			setTimeout(() => {func()}, 500);
		});	
	} catch(e) {
		alert(text);
		func();
	}
}

//SweetAlert2 Custom question method (Legacy)
//ex) createSweetAlert2Question('테스트', '테스트 입니다.', () => { console.log('test'); });
function createSweetAlert2Question (title, text, func) {
	try {
		Swal.fire({
			icon: 'question',
			title: title,
			html: text
		}).then((result) => {
			setTimeout(() => {func()}, 500);
		});	
	} catch(e) {
		alert(text);
		func();
	}
}

//SweetAlert2 Custom success method (Legacy)
//ex) createSweetAlert2Success('테스트', '테스트 입니다.', () => { console.log('test'); });
function createSweetAlert2Success (title, text, func) {
	try {
		Swal.fire({
			icon: 'success',
			title: title,
			html: text
		}).then((result) => {
			setTimeout(() => {func()}, 500);
		});	
	} catch(e) {
		alert(text);
		func();
	}
}

//SweetAlert2 Custom info method (Legacy)
//ex) createSweetAlert2Info('테스트', '테스트 입니다.', () => { console.log('test'); });
function createSweetAlert2Info (title, text, func) {
	try {
		Swal.fire({
			icon: 'info',
			title: title,
			html: text
		}).then((result) => {
			setTimeout(() => {func()}, 500);
		});	
	} catch(e) {
		alert(text);
		func();
	}
}

/**
 * confirm용 기존 코드
 * 
 * @param title						alert 의 제목
 * @param content					alert 의 content 값
 * @param confirmBtnText			YES 의 의미인 버튼 텍스트
 * @param cancelBtnText				NO 의 의미인 버튼 텍스트
 * @param confirmFunc				YES 일 경우 함수 실행
 * 
 * example js source1: createSweetAlert2Confirm('테스트', '테스트 입니다.', '삭제', '취소', () => { console.log('test'); });
 * 
 * @returns void
 */
function createSweetAlert2Confirm(title, content, confirmBtnText, cancelBtnText, confirmFunc) {
	try {
		Swal.fire({
			icon: 'question',
			title: title,
			html: content,
			showDenyButton: true,
			confirmButtonText: confirmBtnText,
			denyButtonText: cancelBtnText,
		}).then((result) => {
			if (result.isConfirmed) {
				confirmFunc();
			} else if (result.isDenied) {
				return;
			} else {
				return;
			}
		});
	} catch(e) {
		if (!confirm(content)){
			return
		}
		confirmFunc();
	}
}


/**
 * confirm용 icon 통합본
 * 
 * @param title						alert 의 제목
 * @param content					alert 의 content 값
 * @param confirmBtnText			YES 의 의미인 버튼 텍스트
 * @param cancelBtnText				NO 의 의미인 버튼 텍스트
 * @param confirmFunc				YES 일 경우 함수 실행
 * @param iconName					icon 타입 ['success', 'error', 'warning', 'info', 'question']
 * 
 * example js source1: createSweetAlert2Confirm('테스트', '테스트 입니다.', '삭제', '취소', () => { console.log('test'); }, null);
 * example js source2: createSweetAlert2Confirm('테스트', '테스트 입니다.', '삭제', '취소', () => { console.log('test'); }, 'info');
 * 
 * @returns void
 */
function createSweetAlert2Confirm(title, content, confirmBtnText, cancelBtnText, confirmFunc, iconName) {
	
	if(iconName == null || iconName == undefined || iconName.trim() == '') {
		iconName = 'info';
	} else {
		switch(iconName.trim()) {
			case 'success':
				iconName = 'success';
				break;
			case 'error':
				iconName = 'error';
				break;
			case 'warning':
				iconName = 'warning';
				break;
			case 'question':
				iconName = 'question';
				break;
			case 'info':
			default:
				iconName = 'info';
		}
	}
	
	try {
		Swal.fire({
			icon: iconName,
			title: title,
			html: content,
			showDenyButton: true,
			confirmButtonText: confirmBtnText,
			denyButtonText: cancelBtnText,
		}).then((result) => {
			if (result.isConfirmed) {
				confirmFunc();
			} else if (result.isDenied) {
				return;
			} else {
				return;
			}
		});
	} catch(e) {
		if (!confirm(content)){
			return
		}
		confirmFunc();
	}
}

//Crownix Viewer js에서 사용하는 sweetalert
function createSweetAlert2RdPwd(verifyFunc, confirmFunc){
	const inputId = "xlspwd";
	
	try{
		Swal.fire({
			icon: 'question',
			titleText: "Excel 파일 비밀번호 설정",
			html: `<div class='align-left'>엑셀 다운로드시 설정할 암호를 입력바랍니다.<br>※ 8자리 이상<br>※ 영문자, 숫자, 특수문자 3가지 혼합<br>※ 특수문자는 @$!%*#?& 만 사용가능합니다.)<div><hr class='flex'>` + 
				`<form onsubmit='return false'><input type='password' id='${inputId}' name='${inputId}' autocomplete='off' style='width:100%;' title='엑셀파일의 비밀번호' placeholder='엑셀파일의 비밀번호'/></form>`,
			showDenyButton: false,
			confirmButtonText: "조회",
			allowOutsideClick: false,
			allowEscapeKey: false,
			preConfirm : () => verifyFunc(inputId)
		}).then(() => {
			confirmFunc(inputId);
		});
	} catch(e) {
		console.log(e);
	}
}