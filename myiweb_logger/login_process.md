1. https://sso.mju.ac.kr/sso/auth?client_id=msi&response_type=code&state=1764333671729&tkn_type=normal&redirect_uri=https%3A%2F%2Fmsi.mju.ac.kr%2Findex_Myiweb.jsp

[로그인 과정 참조](../mju_sso_login.py)

2. 들어가니까 여러번 사이트 url 이 변경되며 최종 https://msi.mju.ac.kr/servlet/security/MySecurityStart 페이지로 이동함.

3. 학생 카드 버튼을 선택 
```
<a class="btn-snb-item" data-url="/servlet/su/sum/Sum00Svl01getStdCard" data-sysdiv="SCH" data-subsysdiv="SCH" data-folderdiv="101" data-pgmid="W_SUD005">학생카드</a>
```

4.  https://msi.mju.ac.kr/servlet/su/sum/Sum00Svl01getStdCard 페이지로 이동, 들어가니까 바로 보이지는 않고
```
<div class="card-item basic">
			<div class="data-title small font-color-blue">
				학생 여러분의 정보를 안전하게 보호하기 위해 암호를 다시 한 번 입력 바랍니다.
			</div>
			
			<form id="command" name="form1" action="/servlet/sys/sys15/Sys15Svl01initPage" method="post" onsubmit="return false;" autocomplete="false">
			<input type="hidden" name="originalurl" value="https://msi.mju.ac.kr/servlet/su/sum/Sum00Svl01getStdCard">
			<div>
				<div class="flex-table">
					<div class="flex-cell grid-1 m-grid-1">
						<div class="flex-table-item">
							<div class="item-title width-per-30 m-width-per-30">
								<div class="flex-align-self-center">
									통합로그인(SSO) 비밀번호
								</div>
							</div>
							<div class="item-data width-per-70 m-width-per-70">
								<div class="flex-align-self-center" id="passworddiv">
									<input type="password" id="pwtext" name="tfpassword" style="ime-mode:disabled;" maxlength="20" placeholder="비밀번호를 입력하세요">
									<button type="button" id="submitpw" class="btn-basic btn-gray btn-small" onclick="javascript:submitData();">확인</button>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
			<div>
<input type="hidden" name="_csrf" value="385c392b-c856-47f9-ade3-45bf830243fe">
</div></form>
		</div>
```
1. 비밀번호 재입력 폼이 나옴, 여기서 다시 비밀번호를 입력해야함. 입력하며

2. 입력하면 여러번 url 이 변경되다가 https://msi.mju.ac.kr/servlet/su/sum/Sum00Svl01getStdCard 페이지로 이동하며 학생카드 정보가 나옴.

여기서 
<div class="card-item basic">
			<div>
				<div id="pictureInclude">
					<div style="display: flex; align-items: center; justify-content: center;">
						<img src="data:image/jpg;base64,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" border="0" width="120" height="120">

					</div>
					
					<div class="flex-table" style="width:100%;">
						<div class="flex-cell grid-2 m-grid-1">
							<div class="flex-table-item">
								<div class="item-title width-per-40 m-width-per-30"><div class="flex-align-self-center">학번</div></div>
								<div class="item-data width-per-60 m-width-per-70 flex-align-self-center"><div>60222100</div></div>
							</div>
						</div>
						<div class="flex-cell grid-2 m-grid-1">
							<div class="flex-table-item">
								<div class="item-title width-per-40 m-width-per-30"><div class="flex-align-self-center">한글성명</div></div>
								<div class="item-data width-per-60 m-width-per-70 flex-align-self-center"><div>신년기</div></div>
							</div>
						</div>
						
						<div class="flex-cell grid-2 m-grid-1">
							<div class="flex-table-item">
								<div class="item-title width-per-40 m-width-per-30"><div class="flex-align-self-center">학년</div></div>
								<div class="item-data width-per-60 m-width-per-70 flex-align-self-center"><div>4 학년</div></div>
							</div>
						</div>
						<div class="flex-cell grid-2 m-grid-1">
							<div class="flex-table-item">
								<div class="item-title width-per-40 m-width-per-30"><div class="flex-align-self-center">학적상태</div></div>
								<div class="item-data width-per-60 m-width-per-70 flex-align-self-center">
									<div class="twowrap">
										<div>재학</div>
										
									</div>
								</div>
							</div>
						</div>
						
						
						
						<div class="flex-cell grid-1 m-grid-1">
							<div class="flex-table-item">
								<div class="item-title width-per-20 m-width-per-30"><div class="flex-align-self-center">학부(과)</div></div>
								<div class="item-data width-per-80 m-width-per-70 flex-align-self-center"><div>(반도체·ICT대학) 컴퓨터정보통신공학부 컴퓨터공학전공</div></div>
							</div>
						</div>
						
						<div class="flex-cell grid-1 m-grid-1">
							<div class="flex-table-item">
								<div class="item-title width-per-20 m-width-per-30"><div class="flex-align-self-center">상담교수</div></div>
								<div class="item-data width-per-80 m-width-per-70 flex-align-self-center"><div>조민경 (컴퓨터정보통신공학부 컴퓨터공학전공)</div></div>
							</div>
						</div>
						
						<div class="flex-cell grid-1 m-grid-1">
							<div class="flex-table-item">
								<div class="item-title width-per-20 m-width-per-30"><div class="flex-align-self-center">학생설계전공지도교수</div></div>
								<div class="item-data width-per-80 m-width-per-70 flex-align-self-center"><div> ()</div></div>
							</div>
						</div>
						
						
						
						
						
						
						
						
						
						
					</div>
					
				</div>
				
				<hr style="display: block;">
					
				<div class="flex-table">
					<div class="flex-cell grid-2 m-grid-1">
						<div class="flex-table-item">
							<div class="item-title width-per-40 m-width-per-30"><div class="flex-align-self-center">영문성명(성)</div></div>
							<div class="item-data width-per-60 m-width-per-70 flex-align-self-center">
								<div class="twowrap">
									<input type="text" name="nm_eng" maxlength="20" value="Shin" placeholder="ex) HONG">
								</div>
							</div>
						</div>
					</div>
					<div class="flex-cell grid-2 m-grid-1">
						<div class="flex-table-item">
							<div class="item-title width-per-40 m-width-per-30"><div class="flex-align-self-center">영문성명(이름)</div></div>
							<div class="item-data width-per-60 m-width-per-70 flex-align-self-center">
								<div class="twowrap">
									<input type="text" name="nm_eng2" maxlength="20" value="Nyeon Ki" placeholder="ex) GIL DONG">
								</div>
							</div>
						</div>
					</div>
						
					<div class="flex-cell grid-2 m-grid-1">
						<div class="flex-table-item">
							<div class="item-title width-per-40 m-width-per-30"><div class="flex-align-self-center">전화번호<span class="essential">*</span></div></div>
							<div class="item-data width-per-60 m-width-per-70 flex-align-self-center">
								<div class="twowrap">
									<input type="text" name="std_tel" class="required" maxlength="20" value="010-9503-1512" placeholder="ex) 000-000-0000">
								</div>
							</div>
						</div>
					</div>
					<div class="flex-cell grid-2 m-grid-1">
						<div class="flex-table-item">
							<div class="item-title width-per-40 m-width-per-30"><div class="flex-align-self-center">휴대폰</div></div>
							<div class="item-data width-per-60 m-width-per-70 flex-align-self-center">
								<div class="twowrap">
									<input type="text" name="htel" maxlength="20" value="01095031512" placeholder="ex) 010-0000-0000">
								</div>
							</div>
						</div>
					</div>
					
					<div class="flex-cell grid-1 m-grid-1">
						<div class="flex-table-item">
							<div class="item-title width-per-20 m-width-per-30"><div class="flex-align-self-center">E-Mail</div></div>
							<div class="item-data width-per-80 m-width-per-70 flex-align-self-center">
								<div class="twowrap">
									<input type="text" name="email" size="20" value="sygys10293@mju.ac.kr" placeholder="ex) example@samplemail.com">
								</div>
							</div>
						</div>
					</div>
					
					<div class="flex-cell grid-1 m-grid-1">
						<div class="flex-table-item">
							<div class="item-title width-per-20 m-width-per-30"><div class="flex-align-self-center">현거주지 주소<span class="essential">*</span></div></div>
							<div class="item-data width-per-80 m-width-per-70 flex-align-self-center">
								<div class="twowrap">
									<div class="zipCodeDiv">
										<input type="text" name="zip1" class="zipCode required" maxlength="3" onclick="javascript:msgHelp()" readonly="" value="136"> -
										<input type="text" name="zip2" class="zipCode required" maxlength="3" onclick="javascript:msgHelp()" readonly="" value="29">
										<img src="/images/btn_search.gif" border="0" onclick="javascript:ZipOpenWindow('1');" style="cursor:pointer" alt="현 거주지 주소 검색" title="현 거주지 주소 검색">
									</div>
									<div class="addressDiv">
										<div class="twowrap">
											<input type="text" name="addr1" class="addressInput" maxlength="100" value="경기도 성남시 분당구 미금일로 22">
											<input type="text" name="addr2" class="addressInput" maxlength="50" value="208동 204호">
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
					
					<div class="flex-cell grid-1 m-grid-1">
						<div class="flex-table-item">
							<div class="item-title width-per-20 m-width-per-30"><div class="flex-align-self-center">주민등록 주소<span class="essential">*</span></div></div>
							<div class="item-data width-per-80 m-width-per-70 flex-align-self-center">
								<div class="twowrap">
									<div class="zipCodeDiv">
										<input type="text" name="zip1_2" class="zipCode required" maxlength="3" onclick="javascript:msgHelp()" readonly="" value="136"> -
										<input type="text" name="zip2_2" class="zipCode required" maxlength="3" onclick="javascript:msgHelp()" readonly="" value="29">
										<img src="/images/btn_search.gif" border="0" onclick="javascript:ZipOpenWindow('2');" style="cursor:pointer" alt="주민등록 주소 검색" title="주민등록 주소 검색">
									</div>
									<div class="addressDiv">
										<div class="twowrap">
											<input type="text" name="addr1_2" class="addressInput" maxlength="100" readonly="" value="경기도 성남시 분당구 미금일로 22">
											<input type="text" name="addr2_2" class="addressInput" maxlength="50" value="208동 204호">
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
					
					<div class="flex-cell grid-1 m-grid-1">
						<div class="flex-table-item">
							<div class="item-title width-per-20 m-width-per-30"><div class="flex-align-self-center">명지포커스 책자 수신여부</div></div>
							<div class="item-data width-per-80 m-width-per-70 flex-align-self-center">
								<div class="twowrap">
									<label>
										<input type="checkbox" name="focus_yn" size="20" value="Y">
										명지포커스 수신허용 및 개인정보 활용에 동의합니다.
									</label>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
```

6. 내용을 파싱하여 학생 정보를 추출하면 됨.