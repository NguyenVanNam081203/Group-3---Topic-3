document.querySelectorAll('select').forEach(selectElement => {
  selectElement.addEventListener('change', function () {
    updateURLFilters();
    checkFilters();  // Kiểm tra lại bộ lọc sau khi thay đổi
  });
});

function updateURLFilters() {
  const url = new URL(window.location.href);
  document.querySelectorAll('select').forEach(selectElement => {
    if (selectElement.value) {
      url.searchParams.set(selectElement.id, selectElement.value);
    } else {
      url.searchParams.delete(selectElement.id);
    }
  });

  // Xóa tham số 'sort-by-distance' nếu có
  url.searchParams.delete('sort-by-distance');

  history.replaceState(null, '', url.toString());
}

function checkFilters() {
  // Luôn hiển thị nút xóa bộ lọc
  const clearButton = document.getElementById('clear-filters');
  clearButton.style.display = 'inline-block';  // Hiển thị nút "xóa bộ lọc"

  // Kiểm tra xem có bất kỳ bộ lọc nào đang được áp dụng không
  const urlParams = new URLSearchParams(window.location.search);
  const hasFilters = Array.from(document.querySelectorAll('select')).some(select => {
    return urlParams.has(select.id) && urlParams.get(select.id).trim() !== '';
  });

  const hasKeyword = urlParams.has('keyword') && urlParams.get('keyword').trim() !== '';

  if (hasFilters || hasKeyword) {
    // Có bộ lọc nào được chọn, có thể làm gì đó nếu cần
  }
}

function clearFilters() {
  document.querySelectorAll('select').forEach(selectElement => {
    selectElement.value = '';  // Đặt giá trị về mặc định
  });

  const url = new URL(window.location.href);
  url.search = ''; // Xóa tất cả tham số bộ lọc
  history.replaceState(null, '', url.toString());
  location.href = '/dashboard';  // Tải lại trang
}

document.addEventListener('DOMContentLoaded', () => {
  restoreFiltersFromURL();
  checkFilters();
});

function restoreFiltersFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  document.querySelectorAll('select').forEach(selectElement => {
    const filterValue = urlParams.get(selectElement.id);
    if (filterValue) {
      selectElement.value = filterValue;  // Áp dụng giá trị từ URL
    } else {
      // Đảm bảo rằng giá trị mặc định (ví dụ "Chọn địa điểm") không được chọn lại
      if (!selectElement.value) {
        selectElement.selectedIndex = 0; // Chọn lại option đầu tiên, ví dụ: "Chọn địa điểm"
      }
    }
  });
}




/*-------------- Bộ lọc tìm kiếm ------------- */
function search() {
  const keyword = document.getElementById('search-keyword').value.trim();
  const url = new URL(window.location.href);

  if (keyword) {
      url.searchParams.set('keyword', keyword);
  } else {
      url.searchParams.delete('keyword');
  }

  // Đặt trang về 1 khi tìm kiếm
  url.searchParams.set('page', 1);

  // Chuyển hướng tới URL đã cập nhật
  window.location.href = url.toString();
}


// Giữ lại giá trị tìm kiếm sau khi tải lại trang
document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const keyword = urlParams.get('keyword');
  if (keyword) {
    document.getElementById('search-keyword').value = keyword;  // Đặt giá trị vào ô tìm kiếm
  }
});

// Xóa bộ lọc (gồm cả tìm kiếm)
function clearFilters() {
  const url = new URL(window.location.href);
  url.searchParams.delete('keyword');  // Xóa tham số 'keyword'
  history.replaceState(null, '', url.toString());

  // Xóa nội dung trong ô tìm kiếm
  document.getElementById('search-keyword').value = '';

  // Tải lại trang
  location.href = '/dashboard';  // Hoặc thay đổi URL tương ứng
}
  

/*--------------------- Bộ lọc theo miền -----------------*/
function filterByRegion() {
  const region = document.getElementById('region-select').value;
  const url = new URL(window.location.href);

  if (region && region !== 'Vùng miền') {
      url.searchParams.set('mien', region);
  } else {
      url.searchParams.delete('mien');
  }

  url.searchParams.set('page', 1);
  // Chuyển hướng tới URL đã cập nhật
  window.location.href = url.toString();
}



/* Bộ lọc địa điểm */
 // Danh sách 63 tỉnh thành Việt Nam
 const provinces = [
  'An Giang', 'Bà Rịa – Vũng Tàu', 'Bắc Giang', 'Bắc Kạn', 'Bạc Liêu', 'Bắc Ninh', 
  'Bến Tre', 'Bình Dương', 'Bình Định', 'Bình Phước', 'Bình Thuận', 'Cà Mau', 
  'Cao Bằng', 'Cần Thơ', 'Đắk Lắk', 'Đắk Nông', 'Điện Biên', 'Đồng Nai', 'Đồng Tháp', 
  'Gia Lai', 'Hà Giang', 'Hà Nam', 'Hà Nội', 'Hà Tĩnh', 'Hải Dương', 'Hải Phòng', 'Hòa Bình', 
  'Hậu Giang', 'Hồ Chí Minh', 'Hưng Yên', 'Khánh Hòa', 'Kiên Giang', 'Kon Tum', 
  'Lai Châu', 'Lâm Đồng', 'Lạng Sơn', 'Lào Cai', 'Long An', 'Nam Định', 'Nghệ An', 
  'Ninh Bình', 'Ninh Thuận', 'Phú Thọ', 'Phú Yên', 'Quảng Bình', 'Quảng Nam', 
  'Quảng Ngãi', 'Quảng Ninh', 'Quảng Trị', 'Sóc Trăng', 'Sơn La', 'Tây Ninh', 
  'Thái Bình', 'Thái Nguyên', 'Thanh Hóa', 'Thừa Thiên – Huế', 'Tiền Giang', 
  'Trà Vinh', 'Tuyên Quang', 'Vĩnh Long', 'Vĩnh Phúc', 'Yên Bái'
];

window.onload = function() {
  const locationSelect = document.getElementById('location-select');

  // Xóa tất cả các option trừ option đầu tiên
  locationSelect.innerHTML = '<option value="">Chọn địa điểm</option>';

  // Thêm các tỉnh thành vào dropdown
  provinces.forEach(province => {
    const option = document.createElement('option');
    option.value = province;
    option.textContent = province;
    locationSelect.appendChild(option);
  });

  // Lấy giá trị 'thanh_pho' từ URL và chọn đúng option
  const urlParams = new URLSearchParams(window.location.search);
  const selectedProvince = urlParams.get('thanh_pho');
  if (selectedProvince) {
    locationSelect.value = selectedProvince;  // Đặt giá trị đã chọn
  }

  // Xử lý sự kiện khi thay đổi lựa chọn
  locationSelect.addEventListener('change', function() {
    const selectedProvince = locationSelect.value;
    if (selectedProvince) {
      // Cập nhật URL và tải lại trang với tham số thanh_pho
      const currentUrl = new URL(window.location.href);
      currentUrl.searchParams.set('thanh_pho', selectedProvince); // Thêm hoặc cập nhật tham số thanh_pho
      window.location.href = currentUrl; // Chuyển hướng đến URL mới
    }
  });
};

/* --------------------- Bộ lọc theo loại mặt bằng ---------------- */
// Hàm lọc các sản phẩm theo loại mặt bằng
document.getElementById('property-type-select').addEventListener('change', function() {
  const selectedType = this.value;
  const url = new URL(window.location.href);

  if (selectedType) {
      url.searchParams.set('loai_mat_bang', selectedType);  // Thêm tham số lọc vào URL
  } else {
      url.searchParams.delete('loai_mat_bang');  // Xóa tham số lọc nếu không chọn loại mặt bằng
  }

  url.searchParams.set('page', 1);

  // Chuyển hướng tới URL mới với tham số lọc
  window.location.href = url.toString();
});

// Giữ lại bộ lọc khi trang tải lại
document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const selectedType = urlParams.get('loai_mat_bang');
  if (selectedType) {
      document.getElementById('property-type-select').value = selectedType;  // Đặt giá trị đã chọn trong dropdown
  }

  // Lọc sản phẩm hiển thị khi trang tải lại
  filterProducts(selectedType);
});

// Lọc các sản phẩm hiển thị theo loại mặt bằng
function filterProducts(selectedType) {
  const products = document.querySelectorAll('.product-item');
  
  products.forEach(product => {
      const productType = product.querySelector('.product-type').textContent.trim();
      
      // Nếu sản phẩm không khớp với loại mặt bằng được chọn, ẩn sản phẩm
      if (selectedType && productType !== selectedType) {
          product.style.display = 'none';
      } else {
          product.style.display = 'block';  // Hiển thị sản phẩm nếu khớp
      }
  });
}

/* ----------------------------Bộ lọc giá --------------------- */
// Bộ lọc giá
document.getElementById('price-select').addEventListener('change', function() {
  const selectedPriceRange = this.value;
  const url = new URL(window.location.href);

  // Cập nhật tham số 'price' trong URL với giá trị được chọn
  if (selectedPriceRange) {
      url.searchParams.set('price', selectedPriceRange);  // Thêm tham số lọc giá vào URL
  } else {
      url.searchParams.delete('price');  // Nếu không có lựa chọn, xóa tham số lọc giá
  }

    // Đặt trang về 1 khi tìm kiếm
    url.searchParams.set('page', 1);

  // Cập nhật URL và tải lại trang với tham số lọc giá
  window.location.href = url.toString();  // Chuyển hướng đến URL mới
});

// Giữ lại giá trị của dropdown khi trang tải lại
document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const selectedPrice = urlParams.get('price');
  
  // Nếu có tham số 'price', đặt giá trị cho dropdown
  if (selectedPrice) {
      document.getElementById('price-select').value = selectedPrice;
  }
});


/*--------------- Lọc theo Diện tích mặt bằng -------------------*/
// Bộ lọc diện tích mặt bằng
// Lắng nghe sự kiện thay đổi trên dropdown diện tích
document.getElementById('area-select').addEventListener('change', function () {
  const selectedAreaRange = this.value;
  const url = new URL(window.location.href);

  // Cập nhật tham số 'area' trong URL với giá trị được chọn
  if (selectedAreaRange) {
    url.searchParams.set('area', selectedAreaRange); // Thêm tham số lọc diện tích vào URL
  } else {
    url.searchParams.delete('area'); // Nếu không có lựa chọn, xóa tham số lọc diện tích
  }

  // Đặt lại trang về 1 khi thay đổi bộ lọc
  url.searchParams.set('page', 1);

  // Chuyển hướng đến URL mới
  window.location.href = url.toString();
});

// Giữ lại giá trị của dropdown khi trang tải lại
document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const selectedArea = urlParams.get('area');

  // Nếu có tham số 'area', đặt giá trị cho dropdown
  if (selectedArea) {
    document.getElementById('area-select').value = selectedArea;
  }
});


/* -------------------- chat bot ------------------------------*/
document.addEventListener('DOMContentLoaded', function() {
  const chatbotIcon = document.getElementById('chatbot-icon');
  const chatbox = document.getElementById('chatbox');
  const closeChatbox = document.getElementById('close-chatbox');
  const sendMessageButton = document.getElementById('send-message-button'); // Lấy đúng phần tử button
  const userMessageInput = document.getElementById('user-message-input'); // Lấy đúng phần tử input
  const chatContent = document.getElementById('chat-content'); // Lấy đúng phần tử chat

  // Hiển thị chatbox khi nhấn vào biểu tượng
  chatbotIcon.addEventListener('click', () => {
    chatbox.classList.toggle('hidden');
  });

  // Đóng chatbox khi nhấn vào nút đóng
  closeChatbox.addEventListener('click', () => {
    chatbox.classList.add('hidden');
  });

  // Gửi tin nhắn khi nhấn nút "Gửi"
  sendMessageButton.addEventListener('click', async () => {
    const userMessage = userMessageInput.value.trim();
    if (!userMessage) return;

    // Hiển thị tin nhắn người dùng
    chatContent.innerHTML += `<div class="text-gray-600">Bạn: ${userMessage}</div>`;
    userMessageInput.value = ''; // Xóa input

    // Gửi yêu cầu đến backend
    const response = await fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
    });

    const data = await response.json();

    if (data.response) {
        // Kiểm tra nếu phản hồi chứa HTML (ảnh hoặc văn bản)
        const botMessageElem = document.createElement('div');
        botMessageElem.classList.add('text-blue-600');
        if (data.response.includes('<img')) {
            botMessageElem.innerHTML = `Bot: ${data.response}`;
        } else {
            botMessageElem.textContent = `Bot: ${data.response}`;
        }
        chatContent.appendChild(botMessageElem);
    } else {
        chatContent.innerHTML += `<div class="text-red-600">Có lỗi xảy ra: ${data.error}</div>`;
    }

    // Cuộn xuống cuối chatbox
    chatContent.scrollTop = chatContent.scrollHeight;
});

  // Gửi tin nhắn khi ấn phím Enter
  userMessageInput.addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
      const userMessage = userMessageInput.value.trim();
      if (!userMessage) return; // Nếu không có tin nhắn, không làm gì

      // Hiển thị tin nhắn người dùng trong chatbox
      chatContent.innerHTML += `<div class="text-gray-600">Bạn: ${userMessage}</div>`;
      userMessageInput.value = ''; // Xóa input

      // Gửi yêu cầu đến backend để nhận phản hồi từ Cohere
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await response.json();

      if (data.response) {
        // Hiển thị phản hồi của bot
        chatContent.innerHTML += `<div class="text-blue-600">Bot: ${data.response}</div>`;
      } else {
        chatContent.innerHTML += `<div class="text-red-600">Có lỗi xảy ra: ${data.error}</div>`;
      }

      // Cuộn xuống cuối chatbox
      chatContent.scrollTop = chatContent.scrollHeight;
    }
  });
});



// /*-------------- Giá cả cao - thấp  --------------------*/

const sortByPrice = document.getElementById('sort-by-price');
const resetButton = document.getElementById('reset-price');

// Khi thay đổi lựa chọn sắp xếp
sortByPrice.addEventListener('change', function () {
  const sortOrder = this.value;

  if (sortOrder) {
    // Lấy URL hiện tại và thêm/thay đổi tham số sort_order
    const url = new URL(window.location.href);
    url.searchParams.set('sort_order', sortOrder);
    url.searchParams.set('page', 1); // Quay về trang 1 khi thay đổi sắp xếp
    window.location.href = url.toString();
  }
});

// Nút đặt lại bộ lọc
resetButton.addEventListener('click', function () {
  // Lấy URL hiện tại và xóa tham số sort_order
  const url = new URL(window.location.href);
  url.searchParams.delete('sort_order');
  url.searchParams.set('page', 1); // Quay về trang 1
  window.location.href = url.toString();
});


/* ---------------- khoảng cách -------------------- */







