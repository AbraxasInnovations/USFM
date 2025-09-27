export default function Footer() {
  console.log('Footer component is rendering!')
  return (
    <footer className="bg-gray-800 text-white mt-16">
      <div className="w-full px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="col-span-1 md:col-span-2">
            <h3 className="text-lg font-semibold text-white mb-4">US Finance Moves</h3>
            <p className="text-gray-300 text-sm leading-relaxed mb-4">
              Your comprehensive source for US financial deal news, including M&A, LBO, regulatory actions, 
              and capital market developments. Stay informed with real-time updates on the deals that shape 
              the financial landscape.
            </p>
            <div className="text-xs text-gray-400">
              © 2024 US Finance Moves. All rights reserved.
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-4">Sections</h4>
            <ul className="space-y-2">
              <li>
                <a href="/section/ma" className="text-sm text-gray-300 hover:text-white transition-colors">
                  Mergers & Acquisitions
                </a>
              </li>
              <li>
                <a href="/section/lbo" className="text-sm text-gray-300 hover:text-white transition-colors">
                  LBO & Private Equity
                </a>
              </li>
              <li>
                <a href="/section/reg" className="text-sm text-gray-300 hover:text-white transition-colors">
                  Regulatory
                </a>
              </li>
              <li>
                <a href="/section/cap" className="text-sm text-gray-300 hover:text-white transition-colors">
                  Capital Markets
                </a>
              </li>
              <li>
                <a href="/section/rumor" className="text-sm text-gray-300 hover:text-white transition-colors">
                  DeFi/Crypto
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-4">Resources</h4>
            <ul className="space-y-2">
              <li>
                <a href="/search" className="text-sm text-gray-300 hover:text-white transition-colors">
                  Search
                </a>
              </li>
              <li>
                <a href="/archive" className="text-sm text-gray-300 hover:text-white transition-colors">
                  Archive
                </a>
              </li>
              <li>
                <a href="https://www.sec.gov/edgar" target="_blank" rel="noopener nofollow" className="text-sm text-gray-300 hover:text-white transition-colors">
                  SEC EDGAR
                </a>
              </li>
              <li>
                <a href="https://www.ftc.gov/news-events" target="_blank" rel="noopener nofollow" className="text-sm text-gray-300 hover:text-white transition-colors">
                  FTC News
                </a>
              </li>
              <li>
                <a href="https://www.justice.gov/atr" target="_blank" rel="noopener nofollow" className="text-sm text-gray-300 hover:text-white transition-colors">
                  DOJ Antitrust
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-700 mt-8 pt-6">
          <div className="flex flex-col sm:flex-row justify-between items-center">
            <div className="text-xs text-gray-400 mb-4 sm:mb-0">
              Data sourced from SEC EDGAR, government agencies, and financial news providers.
            </div>
            <div className="text-xs text-gray-400">
              Last updated: {new Date().toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}
