// Cấu hình Tailwind
tailwind.config = {
  darkMode: 'class',
  theme: {
      extend: {
          colors: {
              primary: {
                  "50": "#eff6ff",
                  "100": "#dbeafe",
                  "200": "#bfdbfe",
                  "300": "#93c5fd",
                  "400": "#60a5fa",
                  "500": "#3b82f6",
                  "600": "#2563eb",
                  "700": "#1d4ed8",
                  "800": "#1e40af",
                  "900": "#1e3a8a",
                  "950": "#172554"
              }
          }
      },
      fontFamily: {
          'body': [
              'Inter', 
              'ui-sans-serif', 
              'system-ui', 
              '-apple-system', 
              'system-ui', 
              'Segoe UI', 
              'Roboto', 
              'Helvetica Neue', 
              'Arial', 
              'Noto Sans', 
              'sans-serif', 
              'Apple Color Emoji', 
              'Segoe UI Emoji', 
              'Segoe UI Symbol', 
              'Noto Color Emoji'
          ],
          'sans': [
              'Inter', 
              'ui-sans-serif', 
              'system-ui', 
              '-apple-system', 
              'system-ui', 
              'Segoe UI', 
              'Roboto', 
              'Helvetica Neue', 
              'Arial', 
              'Noto Sans', 
              'sans-serif', 
              'Apple Color Emoji', 
              'Segoe UI Emoji', 
              'Segoe UI Symbol', 
              'Noto Color Emoji'
          ]
      }
  }
};


let container = document.getElementById('container');
let count = 50;
for(var i = 0; i<50; i++){
    let leftSnow = Math.floor(Math.random() * container.clientWidth);
    let topSnow = Math.floor(Math.random() * container.clientHeight);
    let widthSnow = Math.floor(Math.random() * 50);
    let timeSnow = Math.floor((Math.random() * 5) + 5);
    let blurSnow = Math.floor(Math.random() * 10);
    console.log(leftSnow);
    let div = document.createElement('div');
    div.classList.add('snow');
    div.style.left = leftSnow + 'px';
    div.style.top = topSnow + 'px';
    div.style.width = widthSnow + 'px';
    div.style.height = widthSnow + 'px';
    div.style.animationDuration = timeSnow + 's';
    div.style.filter = "blur(" + blurSnow + "px)";
    container.appendChild(div);
}

  // Xử lý sự kiện hiển thị/ẩn mật khẩu
  const togglePassword = document.getElementById('togglePassword');
  const passwordField = document.getElementById('password');
  
  // Chức năng để toggle (mở/ẩn) mắt
  togglePassword.addEventListener('click', function() {
      if (passwordField.type === 'password') {
          passwordField.type = 'text'; // Hiển thị mật khẩu
          togglePassword.querySelector('i').classList.remove('fa-eye-slash');
          togglePassword.querySelector('i').classList.add('fa-eye');
      } else {
          passwordField.type = 'password'; // Ẩn mật khẩu
          togglePassword.querySelector('i').classList.remove('fa-eye');
          togglePassword.querySelector('i').classList.add('fa-eye-slash');
      }
  });


  
