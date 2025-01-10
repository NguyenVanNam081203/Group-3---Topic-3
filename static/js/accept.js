   // Lấy các phần tử
   const header = document.getElementById('header');
   const postReviewSection = document.getElementById('post-review-section');
   const userContactSection = document.getElementById('user-contact-section');
   const pageContent = document.getElementById('page-content');

   // Chuyển đến Post Quảng Bá
   document.getElementById('post-review').addEventListener('click', () => {
       header.textContent = 'Post Quảng Bá';
       postReviewSection.style.display = 'block'; // Hiển thị Post Quảng Bá
       userContactSection.style.display = 'none'; // Ẩn User Nhờ Liên Hệ
       pageContent.style.display = 'none'; // Ẩn Welcome Message
   });

   // Chuyển đến User Nhờ Liên Hệ
   document.getElementById('user-contact').addEventListener('click', () => {
       header.textContent = 'User Nhờ Liên Hệ';
       postReviewSection.style.display = 'none'; // Ẩn Post Quảng Bá
       userContactSection.style.display = 'block'; // Hiển thị User Nhờ Liên Hệ
       pageContent.style.display = 'none'; // Ẩn Welcome Message
   });