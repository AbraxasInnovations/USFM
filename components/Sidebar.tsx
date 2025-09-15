export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="market-data">
        <h3>Market Data</h3>
        <div className="data-item">
          <span className="symbol">DOW</span>
          <span className="price">38,245.67</span>
          <span className="change positive">+2.3%</span>
        </div>
        <div className="data-item">
          <span className="symbol">S&P 500</span>
          <span className="price">4,987.12</span>
          <span className="change positive">+1.8%</span>
        </div>
        <div className="data-item">
          <span className="symbol">NASDAQ</span>
          <span className="price">15,678.34</span>
          <span className="change positive">+2.1%</span>
        </div>
      </div>

      <div className="trending">
        <h3>Trending</h3>
        <ul>
          <li><a href="#">Federal Reserve Policy</a></li>
          <li><a href="#">AI Stock Rally</a></li>
          <li><a href="#">Housing Market Update</a></li>
          <li><a href="#">Energy Sector Outlook</a></li>
          <li><a href="#">Retail Earnings Season</a></li>
        </ul>
      </div>
    </aside>
  )
}
