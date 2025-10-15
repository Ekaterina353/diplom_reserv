import React, { useState, useEffect } from "react";

const App = () => {
  const [activePage, setActivePage] = useState("main");
  const [user, setUser] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [bookingForm, setBookingForm] = useState({
    name: "",
    phone: "",
    date: "",
    time: "",
    guests: 1,
  });

  // Mock data for team members
  const teamMembers = [
    { name: "Анастасия", role: "Шеф-повар", bio: "Специалист по традиционной литовской кухне с 10-летним опытом." },
    { name: "Максим", role: "Управляющий", bio: "Организатор мероприятий и эксперт в гостеприимстве." },
    { name: "Ирина", role: "Сомелье", bio: "Знаток балтийских вин и национальных напитков." }
  ];

  // Mock content for pages
  const pageContent = {
    main: {
      title: "Добро пожаловать в Žemaičiai",
      description: "Ресторан литовской кухни в Краснодаре. Мы предлагаем аутентичные блюда региона Жемайтия и уютную атмосферу литовского гостеприимства.",
      services: [
        "Традиционная литовская кухня",
        "Бронирование столиков",
        "Кейтеринговые услуги",
        "Проведение тематических вечеров"
      ],
      contact: {
        address: "ул. Красная, 123, Краснодар",
        phone: "+7 (988) 123-45-67",
        email: "info@zemaiciai.ru",
        hours: "Ежедневно с 10:00 до 22:00"
      }
    },
    about: {
      title: "О ресторане",
      history: "Ресторан Žemaičiai был основан в 2024 году с целью приблизить жителей Краснодара к богатой культуре Литвы. Название происходит от древнего региона Дзукия на юге Литвы.",
      mission: "Познакомить российскую публику с разнообразием литовской кухни и культуры через вкус, интерьер и обслуживание.",
      values: [
        "Сохранение традиций",
        "Качество ингредиентов",
        "Гостеприимство",
        "Экологичность"
      ]
    }
  };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setBookingForm((prev) => ({ ...prev, [name]: value }));
  };

  // Submit booking form
  const submitBooking = (e) => {
    e.preventDefault();
    const newBooking = {
      id: bookings.length + 1,
      ...bookingForm,
      status: "Подтверждено",
    };
    setBookings([...bookings, newBooking]);
    alert("Ваш столик забронирован!");
    setBookingForm({
      name: "",
      phone: "",
      date: "",
      time: "",
      guests: 1,
    });
  };

  // Render navigation
  const renderNav = () => (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
      <div className="container">
        <a className="navbar-brand" href="#" onClick={() => setActivePage("main")}>
          <strong>Žemaičiai</strong>
        </a>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto">
            <li className="nav-item">
              <a className="nav-link" href="#" onClick={() => setActivePage("main")}>
                Главная
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="#" onClick={() => setActivePage("about")}>
                О ресторане
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="#" onClick={() => setActivePage("booking")}>
                Бронирование
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="#" onClick={() => setActivePage("account")}>
                Личный кабинет
              </a>
            </li>
            {!user ? (
              <li className="nav-item">
                <a className="nav-link" href="#" onClick={() => setActivePage("login")}>
                  Вход
                </a>
              </li>
            ) : (
              <li className="nav-item">
                <a className="nav-link" href="#" onClick={() => setActivePage("admin")}>
                  Админка
                </a>
              </li>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );

  // Main Page
  const renderMainPage = () => (
    <section className="py-5">
      <div className="container">
        <div className="row align-items-center">
          <div className="col-md-6 mb-4 mb-md-0">
            <h1 className="display-5 fw-bold text-primary">{pageContent.main.title}</h1>
            <p className="lead">{pageContent.main.description}</p>
            <h5>Наши услуги:</h5>
            <ul className="list-group list-group-flush">
              {pageContent.main.services.map((service, index) => (
                <li key={index} className="list-group-item bg-transparent border-0">
                  <i className="bi bi-check-circle-fill text-primary me-2"></i>
                  {service}
                </li>
              ))}
            </ul>
          </div>
          <div className="col-md-6">
            <img src="https://picsum.photos/600/400?random=1" alt="Restaurant Interior" className="img-fluid rounded shadow" />
          </div>
        </div>

        <hr className="my-5" />

        <div className="row">
          <div className="col-md-6">
            <h4>Контактная информация</h4>
            <address>
              <p><i className="bi bi-geo-alt-fill text-primary me-2"></i>{pageContent.main.contact.address}</p>
              <p><i className="bi bi-telephone-fill text-primary me-2"></i>{pageContent.main.contact.phone}</p>
              <p><i className="bi bi-envelope-fill text-primary me-2"></i>{pageContent.main.contact.email}</p>
              <p><i className="bi bi-clock-fill text-primary me-2"></i>{pageContent.main.contact.hours}</p>
            </address>
          </div>
          <div className="col-md-6">
            <h4>Форма обратной связи</h4>
            <form>
              <div className="mb-3">
                <label htmlFor="name" className="form-label">Имя</label>
                <input type="text" className="form-control" id="name" placeholder="Ваше имя" />
              </div>
              <div className="mb-3">
                <label htmlFor="email" className="form-label">Email</label>
                <input type="email" className="form-control" id="email" placeholder="Ваш email" />
              </div>
              <div className="mb-3">
                <label htmlFor="message" className="form-label">Сообщение</label>
                <textarea className="form-control" id="message" rows="3" placeholder="Ваше сообщение"></textarea>
              </div>
              <button type="submit" className="btn btn-primary">Отправить</button>
            </form>
          </div>
        </div>
      </div>
    </section>
  );

  // About Page
  const renderAboutPage = () => (
    <section className="py-5 bg-light">
      <div className="container">
        <h2 className="text-center mb-4 text-primary">{pageContent.about.title}</h2>
        <div className="row">
          <div className="col-md-6 mb-4">
            <h4>История ресторана</h4>
            <p>{pageContent.about.history}</p>
          </div>
          <div className="col-md-6 mb-4">
            <h4>Наша миссия</h4>
            <p>{pageContent.about.mission}</p>
            <ul className="list-group">
              {pageContent.about.values.map((value, index) => (
                <li key={index} className="list-group-item d-flex align-items-center">
                  <i className="bi bi-diamond-fill text-primary me-2"></i>
                  {value}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <h4 className="mt-5 mb-3">Наша команда</h4>
        <div className="row g-4">
          {teamMembers.map((member, index) => (
            <div className="col-md-4" key={index}>
              <div className="card h-100 border-primary shadow-sm">
                <img src={`https://picsum.photos/400/300?random=${index+2}`} alt={member.name} className="card-img-top" />
                <div className="card-body">
                  <h5 className="card-title">{member.name}</h5>
                  <h6 className="card-subtitle text-muted mb-2">{member.role}</h6>
                  <p className="card-text">{member.bio}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );

  // Booking Page
  const renderBookingPage = () => (
    <section className="py-5">
      <div className="container">
        <h2 className="text-center mb-4 text-primary">Бронирование столика</h2>
        <div className="row justify-content-center">
          <div className="col-md-8">
            <form onSubmit={submitBooking}>
              <div className="mb-3">
                <label htmlFor="name" className="form-label">Имя</label>
                <input
                  type="text"
                  className="form-control"
                  id="name"
                  name="name"
                  value={bookingForm.name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="phone" className="form-label">Телефон</label>
                <input
                  type="tel"
                  className="form-control"
                  id="phone"
                  name="phone"
                  value={bookingForm.phone}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="date" className="form-label">Дата</label>
                <input
                  type="date"
                  className="form-control"
                  id="date"
                  name="date"
                  value={bookingForm.date}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="time" className="form-label">Время</label>
                <input
                  type="time"
                  className="form-control"
                  id="time"
                  name="time"
                  value={bookingForm.time}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="mb-3">
                <label htmlFor="guests" className="form-label">Количество гостей</label>
                <input
                  type="number"
                  className="form-control"
                  id="guests"
                  name="guests"
                  min="1"
                  max="20"
                  value={bookingForm.guests}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary w-100">Забронировать</button>
            </form>
          </div>
        </div>

        <h3 className="mt-5 mb-4 text-center text-primary">Ваши бронирования</h3>
        {bookings.length === 0 ? (
          <p className="text-center">У вас нет активных бронирований.</p>
        ) : (
          <div className="table-responsive">
            <table className="table table-hover align-middle">
              <thead>
                <tr>
                  <th scope="col">#</th>
                  <th scope="col">Имя</th>
                  <th scope="col">Дата</th>
                  <th scope="col">Время</th>
                  <th scope="col">Гости</th>
                  <th scope="col">Статус</th>
                  <th scope="col">Действия</th>
                </tr>
              </thead>
              <tbody>
                {bookings.map((booking) => (
                  <tr key={booking.id}>
                    <td>{booking.id}</td>
                    <td>{booking.name}</td>
                    <td>{booking.date}</td>
                    <td>{booking.time}</td>
                    <td>{booking.guests}</td>
                    <td>
                      <span className="badge bg-success">{booking.status}</span>
                    </td>
                    <td>
                      <button className="btn btn-sm btn-outline-secondary me-2">Изменить</button>
                      <button className="btn btn-sm btn-outline-danger">Отменить</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );

  // Account Page
  const renderAccountPage = () => (
    <section className="py-5">
      <div className="container">
        <h2 className="text-center mb-4 text-primary">Личный кабинет</h2>
        {!user ? (
          <div className="row justify-content-center">
            <div className="col-md-6">
              <div className="card shadow-sm">
                <div className="card-body">
                  <h4 className="card-title text-center mb-4">Вход</h4>
                  <form>
                    <div className="mb-3">
                      <label htmlFor="loginEmail" className="form-label">Email</label>
                      <input type="email" className="form-control" id="loginEmail" placeholder="Введите ваш email" />
                    </div>
                    <div className="mb-3">
                      <label htmlFor="loginPassword" className="form-label">Пароль</label>
                      <input type="password" className="form-control" id="loginPassword" placeholder="Введите пароль" />
                    </div>
                    <button type="submit" className="btn btn-primary w-100">Войти</button>
                    <hr />
                    <p className="text-center mt-3">
                      Нет аккаунта?{" "}
                      <a href="#" onClick={() => setActivePage("register")} className="text-primary fw-bold">
                        Зарегистрироваться
                      </a>
                    </p>
                  </form>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="row">
            <div className="col-md-4 mb-4">
              <div className="card shadow-sm h-100">
                <div className="card-body text-center">
                  <img src="https://picsum.photos/200/200" alt="User Avatar" className="rounded-circle mb-3" width="100" />
                  <h5 className="card-title">{user.name}</h5>
                  <p className="card-text text-muted">{user.email}</p>
                  <button className="btn btn-outline-danger btn-sm">Выйти</button>
                </div>
              </div>
            </div>
            <div className="col-md-8">
              <h4>История бронирований</h4>
              {bookings.length === 0 ? (
                <p>У вас нет истории бронирований.</p>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Дата</th>
                        <th>Время</th>
                        <th>Гости</th>
                        <th>Статус</th>
                      </tr>
                    </thead>
                    <tbody>
                      {bookings.map((booking) => (
                        <tr key={booking.id}>
                          <td>{booking.id}</td>
                          <td>{booking.date}</td>
                          <td>{booking.time}</td>
                          <td>{booking.guests}</td>
                          <td>
                            <span className="badge bg-success">{booking.status}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </section>
  );

  // Login/Register Switcher
  const renderLoginOrRegister = () => {
    if (activePage === "login") {
      return (
        <section className="py-5">
          <div className="container">
            <div className="row justify-content-center">
              <div className="col-md-6">
                <div className="card shadow-sm">
                  <div className="card-body">
                    <h4 className="card-title text-center mb-4">Вход</h4>
                    <form>
                      <div className="mb-3">
                        <label htmlFor="loginEmail" className="form-label">Email</label>
                        <input type="email" className="form-control" id="loginEmail" placeholder="Введите ваш email" />
                      </div>
                      <div className="mb-3">
                        <label htmlFor="loginPassword" className="form-label">Пароль</label>
                        <input type="password" className="form-control" id="loginPassword" placeholder="Введите пароль" />
                      </div>
                      <button type="submit" className="btn btn-primary w-100">Войти</button>
                      <hr />
                      <p className="text-center mt-3">
                        Нет аккаунта?{" "}
                        <a href="#" onClick={() => setActivePage("register")} className="text-primary fw-bold">
                          Зарегистрироваться
                        </a>
                      </p>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      );
    }

    if (activePage === "register") {
      return (
        <section className="py-5">
          <div className="container">
            <div className="row justify-content-center">
              <div className="col-md-6">
                <div className="card shadow-sm">
                  <div className="card-body">
                    <h4 className="card-title text-center mb-4">Регистрация</h4>
                    <form>
                      <div className="mb-3">
                        <label htmlFor="regName" className="form-label">Имя</label>
                        <input type="text" className="form-control" id="regName" placeholder="Ваше имя" />
                      </div>
                      <div className="mb-3">
                        <label htmlFor="regEmail" className="form-label">Email</label>
                        <input type="email" className="form-control" id="regEmail" placeholder="Введите ваш email" />
                      </div>
                      <div className="mb-3">
                        <label htmlFor="regPassword" className="form-label">Пароль</label>
                        <input type="password" className="form-control" id="regPassword" placeholder="Придумайте пароль" />
                      </div>
                      <div className="mb-3">
                        <label htmlFor="regConfirmPassword" className="form-label">Подтвердите пароль</label>
                        <input
                          type="password"
                          className="form-control"
                          id="regConfirmPassword"
                          placeholder="Повторите пароль"
                        />
                      </div>
                      <button type="submit" className="btn btn-primary w-100">Зарегистрироваться</button>
                      <hr />
                      <p className="text-center mt-3">
                        Уже есть аккаунт?{" "}
                        <a href="#" onClick={() => setActivePage("login")} className="text-primary fw-bold">
                          Войти
                        </a>
                      </p>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      );
    }

    return null;
  };

  // Admin Panel
  const renderAdminPanel = () => (
    <section className="py-5 bg-light">
      <div className="container">
        <h2 className="text-center mb-4 text-primary">Админка</h2>
        <div className="row g-4">
          <div className="col-md-4">
            <div className="card shadow-sm h-100">
              <div className="card-body">
                <h5 className="card-title">Управление пользователями</h5>
                <p className="card-text">Добавляйте, редактируйте или удаляйте пользователей системы.</p>
                <button className="btn btn-outline-primary btn-sm">Перейти</button>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card shadow-sm h-100">
              <div className="card-body">
                <h5 className="card-title">Управление бронированиями</h5>
                <p className="card-text">Просматривайте и управляйте всеми бронированиями в системе.</p>
                <button className="btn btn-outline-primary btn-sm">Перейти</button>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card shadow-sm h-100">
              <div className="card-body">
                <h5 className="card-title">Управление контентом</h5>
                <p className="card-text">Редактируйте тексты, изображения и другие элементы сайта.</p>
                <button className="btn btn-outline-primary btn-sm">Перейти</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );

  // Footer
  const renderFooter = () => (
    <footer className="bg-dark text-white py-4">
      <div className="container">
        <div className="row">
          <div className="col-md-4 mb-3 mb-md-0">
            <h5>Контакты</h5>
            <address className="text-white-50">
              <p><i className="bi bi-geo-alt-fill me-2"></i>ул. Красная, 123, Краснодар</p>
              <p><i className="bi bi-telephone-fill me-2"></i>+7 (988) 123-45-67</p>
              <p><i className="bi bi-envelope-fill me-2"></i>info@zemaiciai.ru</p>
            </address>
          </div>
          <div className="col-md-4 mb-3 mb-md-0">
            <h5>Часы работы</h5>
            <p className="text-white-50"><i className="bi bi-clock-fill me-2"></i>Ежедневно с 10:00 до 22:00</p>
          </div>
          <div className="col-md-4 text-md-end">
            <h5>Соцсети</h5>
            <div className="d-flex gap-3">
              <a href="#" className="text-white">
                <i className="bi bi-facebook fs-4"></i>
              </a>
              <a href="#" className="text-white">
                <i className="bi bi-instagram fs-4"></i>
              </a>
              <a href="#" className="text-white">
                <i className="bi bi-youtube fs-4"></i>
              </a>
            </div>
          </div>
        </div>
        <hr className="border-white my-4 opacity-25" />
        <p className="text-center text-white-50 mb-0">&copy; 2025 Žemaičiai. Все права защищены.</p>
      </div>
    </footer>
  );

  return (
    <div className="App fade-in">
      {/* Navigation */}
      {renderNav()}

      {/* Page Content */}
      <main>
        {activePage === "main" && renderMainPage()}
        {activePage === "about" && renderAboutPage()}
        {activePage === "booking" && renderBookingPage()}
        {activePage === "account" && renderAccountPage()}
        {(activePage === "login" || activePage === "register") && renderLoginOrRegister()}
        {activePage === "admin" && renderAdminPanel()}
      </main>

      {/* Footer */}
      {renderFooter()}
    </div>
  );
};

export default App; 