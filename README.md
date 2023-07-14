# V0. PetMo
### 프로젝트 기간 : 2023.05.04 ~ ing
---
Original development of Petmo Project.
(PetMo Project seed develop.)

프로젝트 소개 :
지역기반 반려동물 커뮤니티 

![petmo-intro](https://github.com/sliverKi/V0.PetMo/assets/121347506/549b2a20-92c0-4846-8afb-18d44c5a1eb7)

<p align="center">
    <p><p>
    <img src="https://github.com/sliverKi/V0.PetMo/assets/121347506/5c636829-2321-44c4-9003-286db11425d0" width="30%" height="23%">
    <img src="https://github.com/sliverKi/V0.PetMo/assets/121347506/4c3c4cca-ffd2-47b6-94a2-92c4941bd933" width="30%" height="23%">
    <img src="https://github.com/sliverKi/V0.PetMo/assets/121347506/2b298a41-42b4-4921-8fc3-13ba7115e843" width="30%" height="23%">
</p>



## * :bulb: System Architecture
---
![image](https://github.com/sliverKi/V0.PetMo/assets/121347506/d3d461d1-4fcb-4168-b2b6-1afb603425c5)

## * :bulb: ERD 
---
![image](https://github.com/sliverKi/V0.PetMo/assets/121347506/7c3c1917-ec56-4361-91f3-f6490af54cd8)

## * :bulb: 프로젝트 정보
https://docs-myfavor.gitbook.io/v0petmo/

## * :bulb: 주요 기능 
    
### - 로그인 & 로그아웃
   - DB값 검증
   - E-mail 로그인
   - ID, PW 일치 불일치 검증 
   - PW 변경
   - 소셜 로그인 (카카오, 네이버)
   - 로그인 시 쿠키(Cookie) 및 세션(Session) 생성
     
### - 내동네 설정
   - [접속하 client ip로 현재 위치 추론하기](https://velog.io/@sliverki/project-Client-IP-%EC%B6%94%EC%A0%81%ED%95%98%EA%B8%B0)
   - client ip를 Geo API에 전달하여 위도, 경도 data 추출
   - client ip에서 위도, 경도 data 추출 후 kakao local Rest-API에 전송하여 지역 data를 서버에 전달  
   - client가 입력한 검색어 기반으로 위치 추론
   - 내 동네 설정의 유효성 검사

### - 반려동물 등록
   - 최대 3마리의 종까지 선택이 가능 (최대로 등록할 수 있는 수 제한 설정)
   - 등록한 반려동물에 대해 변경가능
   
### - 게시글 등록, 댓글 및 대댓글 등록
   - 게시글의 종류와 등록하고자 하는 게시글이 어떤 반려동물에 관한 정보인지 등록후 글 작성 가능
   - 게시글 댓글 및 대댓글 CRUD 가능
   - 게시글 작성자만이 본인의 게시글 수정 삭제 가능
   - 댓글 및 대댓글의 작성자만이 본인이 등록한 댓글 및 대댓글 수정 또는 삭제 가능
   - 조회수, 좋아요수, 북마크 수 표시 

### - 사용자 
   - 본인이 작성한 게시글 또는 댓글을 모아서 조회 가능
   - 프로필 수정 및 변경 가능
   - 등록한 동네 변경 또는 삭제와 반려동물 변경 가능
