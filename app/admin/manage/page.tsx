'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Post } from '@/lib/supabase'

export default function ManageArticles() {
  const [articles, setArticles] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deleteLoading, setDeleteLoading] = useState<string | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    // Check authentication
    const isAuthenticated = sessionStorage.getItem('adminAuth')
    if (!isAuthenticated) {
      router.push('/admin')
      return
    }

    fetchArticles()
  }, [router])

  const fetchArticles = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/admin/articles')
      
      if (!response.ok) {
        throw new Error('Failed to fetch articles')
      }
      
      const { articles } = await response.json()
      setArticles(articles)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (articleId: string) => {
    try {
      setDeleteLoading(articleId)
      const response = await fetch('/api/admin/delete', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ articleId }),
      })

      if (!response.ok) {
        throw new Error('Failed to delete article')
      }

      // Remove the article from the local state
      setArticles(articles.filter(article => article.id !== articleId))
      setDeleteConfirm(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete article')
    } finally {
      setDeleteLoading(null)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-xl text-gray-600">Loading articles...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-6">
        <div className="bg-white shadow-xl rounded-2xl">
          <div className="px-8 py-12">
            {/* Header */}
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Manage Articles</h1>
              <p className="text-xl text-gray-600 mb-6">View and delete uploaded custom articles</p>
              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => router.push('/admin/upload')}
                  className="px-8 py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-200 font-semibold text-lg transition-all"
                >
                  📝 Upload New Article
                </button>
                <button
                  onClick={() => {
                    sessionStorage.removeItem('adminAuth')
                    router.push('/admin')
                  }}
                  className="px-6 py-4 border-2 border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-4 focus:ring-gray-200 font-semibold text-lg transition-all"
                >
                  Logout
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-6 bg-red-50 border-2 border-red-200 rounded-xl">
                <p className="text-red-800 text-lg font-medium">{error}</p>
                <button
                  onClick={() => setError('')}
                  className="mt-2 text-red-600 hover:text-red-800 underline"
                >
                  Dismiss
                </button>
              </div>
            )}

            {/* Articles List */}
            {articles.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📄</div>
                <h3 className="text-2xl font-semibold text-gray-700 mb-2">No Articles Found</h3>
                <p className="text-lg text-gray-500 mb-6">You haven't uploaded any custom articles yet.</p>
                <button
                  onClick={() => router.push('/admin/upload')}
                  className="px-8 py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-200 font-semibold text-lg transition-all"
                >
                  Upload Your First Article
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="text-center">
                  <p className="text-lg text-gray-600">
                    Found <span className="font-semibold text-blue-600">{articles.length}</span> custom article{articles.length !== 1 ? 's' : ''}
                  </p>
                </div>
                
                {articles.map((article) => (
                  <div key={article.id} className="border-2 border-gray-200 rounded-xl p-6 hover:border-gray-300 transition-all">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="text-2xl font-bold text-gray-900 mb-2">
                          {article.title}
                        </h3>
                        <p className="text-lg text-gray-600 mb-3">
                          By <span className="font-semibold">{article.source_name}</span>
                        </p>
                        {article.summary && (
                          <p className="text-gray-700 mb-4 leading-relaxed">
                            {truncateText(article.summary, 200)}
                          </p>
                        )}
                        <div className="flex flex-wrap gap-2 mb-4">
                          {article.tags.map((tag, index) => (
                            <span
                              key={index}
                              className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                        <div className="text-sm text-gray-500">
                          <p>Created: {formatDate(article.created_at)}</p>
                          {article.updated_at !== article.created_at && (
                            <p>Updated: {formatDate(article.updated_at)}</p>
                          )}
                        </div>
                      </div>
                      
                      <div className="ml-6 flex flex-col space-y-3">
                        <button
                          onClick={() => router.push(`/article/${article.article_slug}`)}
                          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-4 focus:ring-green-200 font-medium transition-all"
                        >
                          👁️ View
                        </button>
                        <button
                          onClick={() => setDeleteConfirm(article.id)}
                          disabled={deleteLoading === article.id}
                          className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-4 focus:ring-red-200 font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {deleteLoading === article.id ? '⏳ Deleting...' : '🗑️ Delete'}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Delete Confirmation Modal */}
            {deleteConfirm && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-2xl p-8 max-w-md mx-4">
                  <div className="text-center">
                    <div className="text-6xl mb-4">⚠️</div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-4">Delete Article?</h3>
                    <p className="text-lg text-gray-600 mb-6">
                      This action cannot be undone. The article and its image (if any) will be permanently deleted.
                    </p>
                    <div className="flex space-x-4">
                      <button
                        onClick={() => setDeleteConfirm(null)}
                        className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-4 focus:ring-gray-200 font-medium transition-all"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleDelete(deleteConfirm)}
                        disabled={deleteLoading === deleteConfirm}
                        className="flex-1 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:outline-none focus:ring-4 focus:ring-red-200 font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {deleteLoading === deleteConfirm ? 'Deleting...' : 'Delete'}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
