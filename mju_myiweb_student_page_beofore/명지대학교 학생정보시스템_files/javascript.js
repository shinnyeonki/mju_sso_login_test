function focusElement(element) {
	if (element) {
		element.focus();
		if (element.type == "text" || element.type == "hidden") element.select();
	}
	else {
		alert("JAVA SCRIPT: FOCUS 객체가 존재하지 않습니다.");
		return false;
	}
	return true;
}

function isDD(yyyy, mm, value) {
	var result = false;
	var monthDD = new month_array(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);
	var im = mm - 1;

	//if(value.length != 2) return false;
	if (!isNumber(value)) return false;

	if (isLunnar(yyyy)) {
		monthDD[1] = 29;
	}

	var dd = Number(value);
	if ((0 < dd) && (dd <= monthDD[im])) result = true;
	return result;
}

function isMM(value) {
	return ((value.length > 0) && (isNumber(value)) && (0 < Number(value)) && (Number(value) < 13));
}

function isYYYY(value) {
	return ((value.length == 4) && (isNumber(value)) && (value != "0000"));
}

function DelPreZero(value) {
	var i = 0;

	if (value.length > 1)
		for (i = 0; i < value.length; i++)
			if (value.charAt(i) != '0')
				break;

	return (value.substring(i, value.length));
}

class month_array {
	constructor(m0, m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11) {
		this[0] = m0;
		this[1] = m1;
		this[2] = m2;
		this[3] = m3;
		this[4] = m4;
		this[5] = m5;
		this[6] = m6;
		this[7] = m7;
		this[8] = m8;
		this[9] = m9;
		this[10] = m10;
		this[11] = m11;
	}
}

function Popup(procedure, heightwidth) {
	Win = window.open(procedure, "popup", "toolbar=no,scrollbars=yes,resizable=yes," + heightwidth);
	Win.focus();
}

function trim(value) {
	var str;
	var end;
	for (j = 0; j < value.length; j++) {
		if (value.substring(j, j + 1) != " ") {
			str = j;
			break;
		}
	}
	for (j = value.length - 1; j > -1; j--) {
		if (value.substring(j, j + 1) != " ") {
			end = j;
			break
		}
	}

	return value.substring(str, end + 1);
}

function isNumber(value) {
	value = trim(value);
	value = remove_char(value, ",");
	var result = true;

	for (j = 0; result && (j < value.length); j++) {
		if ((value.substring(j, j + 1) < "0") || (value.substring(j, j + 1) > "9")) {
			if ((value.substring(j, j + 1) == "-") || (value.substring(j, j + 1) == "+")) {
				if (j > 0) { return false; }
			}
			else {
				return false;
			}
		}
	}
	return result;
}

function isNull(value) {
	var chkstr = value + "";
	var result = true;

	if ((chkstr == "") || (chkstr == null)) {
		return result;
	}
	for (j = 0; result && (j < value.length); j++) {
		if (value.substring(j, j + 1) != " ") {
			result = false;
		}
	}

	return result;
}


function IsSSN(value) {
	var v1, v2, v3, v4, v5, v6, v7;
	var v8, v9, v10, v11, v12, v13;
	var v_sum, v_chk;
	var result = false;

	if (value.length == 13) {
		result = true;
		v1 = value.charAt(0);
		v2 = value.charAt(1);
		v3 = value.charAt(2);
		v4 = value.charAt(3);
		v5 = value.charAt(4);
		v6 = value.charAt(5);
		v7 = value.charAt(6);
		v8 = value.charAt(7);
		v9 = value.charAt(8);
		v10 = value.charAt(9);
		v11 = value.charAt(10);
		v12 = value.charAt(11);
		v13 = value.charAt(12);

		v_sum = (parseInt(v1) * 2) + (parseInt(v2) * 3) + (parseInt(v3) * 4) + (parseInt(v4) * 5);
		v_sum = parseInt(v_sum) + (parseInt(v5) * 6) + (parseInt(v6) * 7) + (parseInt(v7) * 8);
		v_sum = parseInt(v_sum) + (parseInt(v8) * 9) + (parseInt(v9) * 2) + (parseInt(v10) * 3);
		v_sum = v_sum + (parseInt(v11) * 4) + (parseInt(v12) * 5);

		v_chk = v_sum % 11;
		v_chk = 11 - v_chk;

		if (v_chk == 11) v_chk = 1
		else if (v_chk == 10) v_chk = 0;

		if (v13 != v_chk) result = false;
	}
	else result = false;


	return result;

}

function IsSSNFocus(value, element) {
	result = IsSSN(value);
	if (!result) {
		focusElement(element);
		alert("?주민번호 등록오류:" + value);
	}
	return result;
}

function NumericEdit(value) {
	var isMinus = false;
	var hasPoint = false;
//	var new_val_rear = "";
	var pure_num = "";
	var new_val = "";
	var below_point = "";
//	var jus_read = "";
	var head_num = 0;
	var loop_count = 0;
	var idx;

	if (value.charAt(0) == '-') isMinus = true;

	for (i = 0; (i < (value.length - 1)) && !hasPoint; i++) {
		if (value.charAt(i) == '.') {
			below_point = value.substring(i, value.length);
			value = value.substring(0, i);
			hasPoint = true;
		}
	}

	for (j = 0; j < (value.length); j++) {
		if ((value.charAt(j) >= '0' &&
			value.charAt(j) <= '9') || value.charAt(j) == '.')
			pure_num = pure_num + value.substr(j, 1);
	}


	if (pure_num.toString().length > 3) {
		head_num = pure_num.length % 3;

		loop_count = (pure_num.toString().length - head_num) / 3;

		if (head_num != 0) new_val = pure_num.substr(0, head_num) + ",";
		new_val = new_val + pure_num.substr(head_num, 3);

		for (idx = 0; idx < (loop_count - 1); idx++) {
			new_val = new_val + ",";
			new_val = new_val + pure_num.substr(head_num + (3 * (idx + 1)), 3);
		}
	}
	else new_val = pure_num;

	if (isMinus) new_val = "-" + new_val;
	if (hasPoint) new_val = new_val + below_point;
	return new_val;
}


function remove_char(str, char1) {
	var pure_num = "";

	for (i = 0; i < (str.length); i++) {
		if (str.charAt(i) != char1)
			pure_num = pure_num + str.substr(i, 1);
	}

	return pure_num;
}

function isLunnar(value) {
	result = false;
	if (isYYYY(value)) {
		if (((value % 4 == 0) && (value % 100 != 0)) || (value % 400 == 0)) {
			result = true;
		}
	}
	return result;
}

function isLunnarFocus(value, element) {
	result = isLunnar(value);
	if (!result) {
		focusElement(element);
		alert("?윤년오류:" + value);
	}
	return result;
}

function alignRight(field) {
	var output = "";
	var spaceN = 0;
	if (field.value.length != field.size) {
		output = remove_char(field.value, " ");
		spaceN = field.size - output.length;
		if (spaceN >= 0) {
			for (j = 0; j < spaceN; j++)  output = " " + output;
		} else {
			output = output.substr(0, field.size);
		}
		field.value = output;

	}
}


var select_val = "" ;

function selectByKey(field) {
	var existMatch = false;
	var sKey = "";
	var KeyCode = event.keyCode;

	if (validKey(KeyCode)) {
		if (KeyCode > 95 && KeyCode < 106) {
			sKey = String.fromCharCode(event.keyCode - 48);
		} else {
			sKey = String.fromCharCode(event.keyCode);
		}
	} else if (KeyCode == 27) {
		select_val = "";
		field.options[0].selected = true
		top.status = "코드를 선택하시거나 직접 입력해 주십시오.";
		return false;
	} else {
		return false;
	}

	select_val += sKey;
	for (var idx = 0; idx < field.length; idx++) {
		if (select_val.length <= field.options[idx].value.length) {
			if (select_val == field.options[idx].value.substring(0, select_val.length)) {
				field.options[idx].selected = true;
				existMatch = true;
				break;
			}
		}
	}
	if (existMatch) {
		top.status = "입력값은 " + select_val + " 입니다. 초기화하시려면 [ESC]를 누르십시오.";
		return true;
	} else {
		top.status = "입력값인 " + select_val + "과 일치하는 항목이 없습니다.코드를 선택하시거나 다시 입력해 주십시오.";
		select_val = select_val.substring(0, select_val.length - 1)
		for (var jdx = 0; jdx < field.length; jdx++) {
			if (select_val.length <= field.options[jdx].value.length) {
				if (select_val == field.options[jdx].value.substring(0, select_val.length)) {
					field.options[jdx].selected = true;
					break;
				}
			}
		}
		select_val = "";
		return false;
	}
}

function selectClear() {
	select_val = "";
	top.status = "";
	return true;
}

function validKey(InputCode) {
	if ((InputCode > 64 && InputCode < 91) ||
		(InputCode > 47 && InputCode < 58) ||
		(InputCode > 95 && InputCode < 106)
	)
		return true;
	else
		return false;
}

//deprecated
function na_preload_img() {
	var img_list = na_preload_img.arguments;
	if (document.preloadlist == null)
		document.preloadlist = new Array();
	var top = document.preloadlist.length;
	for (var i = 0; i < img_list.length; i++) {
		document.preloadlist[top + i] = new Image;
		document.preloadlist[top + i].src = img_list[i + 1];
	}
}


function isLegalDate(value) {
	if (value.length == 10) {
		var year = value.substr(0, 4);
		var bar1 = value.substr(4, 1);
		var month = DelPreZero(value.substr(5, 2));
		var bar2 = value.substr(7, 1);
		var day = DelPreZero(value.substr(8, 2));

		if (bar1 != "-" || bar2 != "-") {
			result = false;
		} else {
			result = isYYYY(year) && isMM(month) && isDD(year, month, day);
		}
	} else {
		result = false;
	}
	return result;
}

function isLegalDateFocus(value, element) {
	result = isLegalDate(value);
	if (!result) {
		focusElement(element);
		alert("일자등록오류:" + value);
	}
	return result;
}

function isMinus(value) {
	var result = false;
	if (value < 0) {
		result = true;
	} else {
		result = false;
	}
	return result;
}

function chkBgtYear(year, date) {
	if (!isLunnar(year)) {
		var begin_date = year + '-03-01';
		var end_date = (((year - 0) + 1) + "") + '-02-28';
	}
	else {
		var begin_date = year + '-03-01';
		var end_date = (((year - 0) + 1) + "") + '-02-29';
	}


	if ((date >= begin_date) && (date <= end_date)) {
		return true;
	}
	else {
		return false;
	}
}

function frmSubmit(frm, sTaskID, sFrame, sUrl) {
	frm.attribute.value = sTaskID;
	frm.target = sFrame;
	frm.action = sUrl;
	frm.submit();
}

function getByteLength(input) {
	/*
	var byteLength = 0;
	for (var inx = 0; inx < input.value.length; inx++) {
		var oneChar = escape(input.value.charAt(inx));
		if (oneChar.length == 1) {
			byteLength++;
		} else if (oneChar.indexOf("%u") != -1) {
			byteLength += 2;
		} else if (oneChar.indexOf("%") != -1) {
			byteLength += oneChar.length / 3;
		}
	}
	return byteLength;
	*/
	
	let byteLength = (function(s,b,i,c){
		for(b=i=0;c=s.charCodeAt(i++);b+=c>>11?3:c>>7?2:1);
		return b
	})(input.value);
	
	return byteLength;
}

function isEmpty(frm, Flds, sMsg) {
	for (i = 0; i < Flds.length; i++) {
		if (frm.elements[Flds[i]].value == null || frm.elements[Flds[i]].value == '') {
			alert(sMsg[i]);
			frm.elements[Flds[i]].focus();
			return true;
		}
	}

	return false;
}

function clearText(frm, Flds)
{
	for (i = 0; i < Flds.length; i++)
		frm.elements[Flds[i]].value = '';
}

//========================================//
function isLegalFromToDt(from,to){

	if (isNull(from.value)) {
		alert("'기간'을 입력하세요");
		from.value = "";
		from.focus();
		return false;
	} else if (!isLegalDate(from.value)) {
		alert("날짜 입력형식에 따라 '기간'을 입력하세요!\n 예:2001-02-03 (2001년 02월 03일)");
		from.value = "";
		from.focus();
		return false;
	}

	if (isNull(to.value)) {
		alert("'기간'을 입력하세요");
		to.value = "";
		to.focus();
		return false;
	} else if (!isLegalDate(to.value)) {
		alert("날짜 입력형식에 따라 '기간'을 입력하세요!\n 예:2001-02-03 (2001년 02월 03일)");
		to.value = "";
		to.focus();
		return false;
	}

	fromDate = from.value.substr(0, 4) + from.value.substr(5, 2) + from.value.substr(8, 2);
	toDate = to.value.substr(0, 4) + to.value.substr(5, 2) + to.value.substr(8, 2);


	if (fromDate > toDate) {
		alert("'기간'이 정확하지 않습니다.");
		to.value = "";
		to.focus();
		return false;
	} else {
		return true;
	}
}

/*
RD 루트경로 호출을 위한 function
*/
function mrd(){
	//var mrd = location.protocol+ "//" + location.host;
	var mrd = "https://rd8.mju.ac.kr:9443/ReportingServer";
	return mrd;
}

/* 특수문사 사용중지 */
function check_event_key() {
	var char_ASCII = event.keyCode;
	if ((char_ASCII>=33 && char_ASCII<=47) || (char_ASCII>=58 && char_ASCII<=64) || (char_ASCII>=91 && char_ASCII<=96) || (char_ASCII>=123 && char_ASCII<=126))	return 1;
}
function SpecialKey() {
	if(check_event_key() == 1) {
		event.returnValue = false;   
		alert("특수문자는 사용할 수 없습니다.");
		return;
	}
}

//우클릭 방지 - alert 주석처리
document.addEventListener("contextmenu", function(e){
	e.preventDefault();
//	alert("마우스 오른쪽 클릭을 사용할 수 없습니다.");
	return false;
}, false);

function PopupCenter(url, title, w, h, frm) {
	// Fixes dual-screen position                         Most browsers      Firefox
	var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
	var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;

	width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
	height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;

	var left = ((width / 2) - (w / 2)) + dualScreenLeft;
	var top = ((height / 2) - (h / 2)) + dualScreenTop;
	var newWindow = window.open("", title, 'scrollbars=yes, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);

	frm.target = title;
	frm.action = url;
	frm.submit();

	// Puts focus on the newWindow
	if (window.focus) {
		newWindow.focus();
	}
}