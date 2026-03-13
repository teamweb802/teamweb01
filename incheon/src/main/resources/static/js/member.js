async function checkId() {
    const idInput = document.getElementById("id");
    const hidden = document.getElementById("id_ck");

    if (!idInput.value.trim()) {
        alert("아이디를 입력하세요.");
        idInput.focus();
        return;
    }

    const response = await fetch(`/member/check-id?id=${encodeURIComponent(idInput.value)}`);
    const result = await response.text();

    if (result === "OK") {
        alert("사용 가능한 아이디입니다.");
        hidden.value = "Y";
    } else {
        alert("이미 사용 중인 아이디입니다.");
        hidden.value = "";
        idInput.focus();
    }
}

async function submitJoin(event) {
    event.preventDefault();

    const form = document.getElementById("join_form");
    const id = document.getElementById("id").value.trim();
    const pw = document.getElementById("pw").value.trim();
    const pw2 = document.getElementById("pw2").value.trim();
    const email = document.getElementById("email").value.trim();
    const idCk = document.getElementById("id_ck").value;

    if (!id) {
        alert("아이디를 입력하세요.");
        return false;
    }

    if (!pw) {
        alert("비밀번호를 입력하세요.");
        return false;
    }

    if (pw !== pw2) {
        alert("비밀번호가 일치하지 않습니다.");
        return false;
    }

    if (!email) {
        alert("이메일을 입력하세요.");
        return false;
    }

    if (idCk !== "Y") {
        alert("아이디 중복 확인을 해주세요.");
        return false;
    }

    const formData = new FormData(form);

    const response = await fetch("/member/join", {
        method: "POST",
        body: formData
    });

    const result = await response.text();

    if (result === "SUCCESS") {
        alert("회원가입이 완료되었습니다.");
        location.href = "/member/login";
        return true;
    } else {
        alert(result);
        return false;
    }
}