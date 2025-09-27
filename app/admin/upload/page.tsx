'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

interface ArticleFormData {
  author: string
  headline: string
  content: string
  summary: string
  tags: string
  image: File | null
  publishDate: string
}

export default function AdminUploadPage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)
  const [formData, setFormData] = useState<ArticleFormData>({
    author: '',
    headline: '',
    content: '',
    summary: '',
    tags: '',
    image: null,
    publishDate: new Date().toISOString().split('T')[0]
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Check authentication on component mount
  useEffect(() => {
    const checkAuth = () => {
      const authStatus = sessionStorage.getItem('adminAuth')
      if (authStatus === 'true') {
        setIsAuthenticated(true)
      } else {
        router.push('/admin')
      }
      setIsCheckingAuth(false)
    }

    checkAuth()
  }, [router])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    setFormData(prev => ({
      ...prev,
      image: file
    }))
  }

  const generateSlug = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError('')
    setSuccess('')

    try {
      // Validate required fields
      if (!formData.author || !formData.headline || !formData.content) {
        throw new Error('Author, headline, and content are required')
      }

      // Create FormData for file upload
      const submitData = new FormData()
      submitData.append('author', formData.author)
      submitData.append('headline', formData.headline)
      submitData.append('content', formData.content)
      submitData.append('summary', formData.summary || formData.content.substring(0, 200) + '...')
      submitData.append('tags', formData.tags)
      submitData.append('publishDate', formData.publishDate)
      submitData.append('articleSlug', generateSlug(formData.headline))
      
      if (formData.image) {
        submitData.append('image', formData.image)
      }

      const response = await fetch('/api/admin/upload', {
        method: 'POST',
        body: submitData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to upload article')
      }

      const result = await response.json()
      setSuccess('Article uploaded successfully!')
      
      // Reset form
      setFormData({
        author: '',
        headline: '',
        content: '',
        summary: '',
        tags: '',
        image: null,
        publishDate: new Date().toISOString().split('T')[0]
      })

      // Redirect to manage page after a short delay
      setTimeout(() => {
        router.push('/admin/manage')
      }, 2000)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsSubmitting(false)
    }
  }

  // Show loading state while checking authentication
  if (isCheckingAuth) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    )
  }

  // Show login redirect if not authenticated
  if (!isAuthenticated) {
    return null // Will redirect to /admin
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-6">
        <div className="bg-white shadow-xl rounded-2xl">
          <div className="px-8 py-12">
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Admin Portal</h1>
              <p className="text-xl text-gray-600 mb-6">Upload custom articles to the Written Articles section</p>
              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => router.push('/admin/manage')}
                  className="px-6 py-3 text-lg text-blue-600 hover:text-blue-800 border-2 border-blue-300 rounded-lg hover:bg-blue-50 transition-colors font-medium"
                >
                  📋 Manage Articles
                </button>
                <button
                  onClick={() => {
                    sessionStorage.removeItem('adminAuth')
                    router.push('/admin')
                  }}
                  className="px-6 py-3 text-lg text-gray-600 hover:text-gray-800 border-2 border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Logout
                </button>
              </div>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            {success && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
                <p className="text-green-800">{success}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Author */}
              <div>
                <label htmlFor="author" className="block text-xl font-semibold text-gray-800 mb-4">
                  Author *
                </label>
                <input
                  type="text"
                  id="author"
                  name="author"
                  value={formData.author}
                  onChange={handleInputChange}
                  required
                  className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all"
                  placeholder="Enter author name"
                />
              </div>

              {/* Headline */}
              <div>
                <label htmlFor="headline" className="block text-xl font-semibold text-gray-800 mb-4">
                  Headline *
                </label>
                <input
                  type="text"
                  id="headline"
                  name="headline"
                  value={formData.headline}
                  onChange={handleInputChange}
                  required
                  className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all"
                  placeholder="Enter article headline"
                />
              </div>

              {/* Summary */}
              <div>
                <label htmlFor="summary" className="block text-xl font-semibold text-gray-800 mb-4">
                  Summary/Excerpt
                </label>
                <textarea
                  id="summary"
                  name="summary"
                  value={formData.summary}
                  onChange={handleInputChange}
                  rows={4}
                  className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all resize-none"
                  placeholder="Enter article summary (optional - will auto-generate if empty)"
                />
              </div>

              {/* Content */}
              <div>
                <label htmlFor="content" className="block text-xl font-semibold text-gray-800 mb-4">
                  Article Content *
                </label>
                <textarea
                  id="content"
                  name="content"
                  value={formData.content}
                  onChange={handleInputChange}
                  required
                  rows={15}
                  className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all resize-none"
                  placeholder="Enter the full article content"
                />
              </div>

              {/* Tags */}
              <div>
                <label htmlFor="tags" className="block text-xl font-semibold text-gray-800 mb-4">
                  Tags
                </label>
                <input
                  type="text"
                  id="tags"
                  name="tags"
                  value={formData.tags}
                  onChange={handleInputChange}
                  className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all"
                  placeholder="Enter tags separated by commas (e.g., finance, analysis, market)"
                />
              </div>

              {/* Image Upload */}
              <div>
                <label htmlFor="image" className="block text-xl font-semibold text-gray-800 mb-4">
                  Featured Image
                </label>
                <input
                  type="file"
                  id="image"
                  name="image"
                  accept="image/*"
                  onChange={handleImageChange}
                  className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all"
                />
                {formData.image && (
                  <div className="mt-4 p-4 bg-green-50 border-2 border-green-200 rounded-xl">
                    <p className="text-lg text-green-800 font-medium">Selected: {formData.image.name}</p>
                  </div>
                )}
              </div>

              {/* Publish Date */}
              <div>
                <label htmlFor="publishDate" className="block text-xl font-semibold text-gray-800 mb-4">
                  Publish Date
                </label>
                <input
                  type="date"
                  id="publishDate"
                  name="publishDate"
                  value={formData.publishDate}
                  onChange={handleInputChange}
                  className="w-full px-6 py-4 text-lg border-2 border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-500 transition-all"
                />
              </div>

              {/* Submit Button */}
              <div className="text-center pt-12 border-t-2 border-gray-200">
                <div className="space-y-6">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full max-w-md mx-auto px-12 py-6 bg-blue-600 text-white rounded-2xl hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-200 disabled:opacity-50 disabled:cursor-not-allowed font-bold text-2xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
                  >
                    {isSubmitting ? 'Uploading...' : '🚀 Upload Article'}
                  </button>
                  <button
                    type="button"
                    onClick={() => router.push('/')}
                    className="px-8 py-4 border-2 border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-4 focus:ring-gray-200 font-semibold text-lg transition-all"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
