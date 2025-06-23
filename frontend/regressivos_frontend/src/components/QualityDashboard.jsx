import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  TestTube, 
  LogOut, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  XCircle,
  Bug,
  Smartphone,
  Monitor,
  ExternalLink
} from 'lucide-react'

const QualityDashboard = ({ user, onLogout }) => {
  const [regressivos, setRegressivos] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchRegressivos()
    // Atualizar a cada 30 segundos para mostrar tempo restante do SLA
    const interval = setInterval(fetchRegressivos, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchRegressivos = async () => {
    try {
      const response = await fetch('/api/quality/regressivos')
      if (response.ok) {
        const data = await response.json()
        setRegressivos(data.data || [])
      }
    } catch (error) {
      console.error('Erro ao buscar regressivos:', error)
      // Dados mock para desenvolvimento
      setRegressivos([
        {
          regressivoId: '1',
          release: 'R113',
          plataforma: 'Android',
          statusGeral: 'ativo',
          liberadoEm: '2025-06-23T12:00:00',
          slaInicio: '2025-06-23T12:00:00',
          slaFim: '2025-06-24T12:00:00',
          versaoHomolog: '2.58.0',
          versaoAlpha: '2.58.1',
          versaoFirebase: '2.58.99',
          tipoRelease: 'Normal',
          linkPlanoTestes: 'https://example.com/plano-testes'
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const fetchStatusResumo = async (regressivoId) => {
    try {
      const response = await fetch(`/api/quality/regressivos/${regressivoId}/status-resumo`)
      if (response.ok) {
        const data = await response.json()
        return data.data
      }
    } catch (error) {
      console.error('Erro ao buscar resumo:', error)
    }
    return {
      total_itens: 10,
      status_count: { 'concluído': 3, 'em andamento': 5, 'bloqueado': 1, 'concluido com bugs': 1 },
      bugs_reportados: 2,
      progresso_percentual: 40
    }
  }

  const calculateTimeRemaining = (slaFim) => {
    if (!slaFim) return null
    
    const now = new Date()
    const end = new Date(slaFim)
    const diff = end - now
    
    if (diff <= 0) return 'SLA Vencido'
    
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
    const seconds = Math.floor((diff % (1000 * 60)) / 1000)
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  const formatDateTime = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString('pt-BR')
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'concluído':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'em andamento':
        return <Clock className="h-4 w-4 text-yellow-600" />
      case 'bloqueado':
        return <XCircle className="h-4 w-4 text-red-600" />
      case 'concluido com bugs':
        return <Bug className="h-4 w-4 text-purple-600" />
      default:
        return <AlertCircle className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusBadge = (status) => {
    const variants = {
      'ativo': 'default',
      'finalizado': 'secondary'
    }
    return <Badge variant={variants[status] || 'default'}>{status}</Badge>
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="ion-header shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center gap-3">
              <TestTube className="h-8 w-8" />
              <div>
                <h1 className="text-xl font-bold">Dashboard de Qualidade</h1>
                <p className="text-sm opacity-90">Ion Regressivos</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm">Olá, {user.name}</span>
              <Button variant="ghost" size="sm" onClick={onLogout}>
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Regressivos Ativos</h2>
          <p className="text-gray-600">Acompanhe e atualize o status dos testes</p>
        </div>

        {regressivos.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <TestTube className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Nenhum regressivo ativo
              </h3>
              <p className="text-gray-600">
                Não há regressivos ativos no momento.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6">
            {regressivos.map((regressivo) => {
              const timeRemaining = calculateTimeRemaining(regressivo.slaFim)
              const isExpired = timeRemaining === 'SLA Vencido'
              
              return (
                <Card key={regressivo.regressivoId} className="ion-card">
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          {regressivo.plataforma === 'Android' ? 
                            <Smartphone className="h-5 w-5 text-green-600" /> : 
                            <Monitor className="h-5 w-5 text-gray-600" />
                          }
                          {regressivo.release} - {regressivo.plataforma}
                        </CardTitle>
                        <CardDescription>
                          Liberado em: {formatDateTime(regressivo.liberadoEm)}
                        </CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        {getStatusBadge(regressivo.statusGeral)}
                        <Badge variant="outline">{regressivo.tipoRelease}</Badge>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    {/* SLA Timer */}
                    {regressivo.slaInicio && (
                      <div className={`mb-4 p-4 rounded-lg ${isExpired ? 'bg-red-50 border border-red-200' : 'bg-blue-50 border border-blue-200'}`}>
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-gray-700">
                              {isExpired ? 'SLA Vencido' : 'Tempo Restante'}
                            </p>
                            <p className={`sla-timer ${isExpired ? 'text-red-600' : 'text-blue-600'}`}>
                              {timeRemaining}
                            </p>
                          </div>
                          {isExpired && (
                            <div className="text-red-600">
                              <AlertCircle className="h-8 w-8" />
                            </div>
                          )}
                        </div>
                        <div className="mt-2 text-xs text-gray-600">
                          SLA: {formatDateTime(regressivo.slaInicio)} - {formatDateTime(regressivo.slaFim)}
                        </div>
                      </div>
                    )}

                    {/* Versões */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-sm font-medium text-gray-500">Versão Homolog</p>
                        <p className="text-sm font-mono">{regressivo.versaoHomolog}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-500">Versão Firebase</p>
                        <p className="text-sm font-mono">{regressivo.versaoFirebase}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-500">Versão Alpha</p>
                        <p className="text-sm font-mono">{regressivo.versaoAlpha}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-500">Plano de Testes</p>
                        {regressivo.linkPlanoTestes ? (
                          <a 
                            href={regressivo.linkPlanoTestes} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                          >
                            Acessar <ExternalLink className="h-3 w-3" />
                          </a>
                        ) : (
                          <p className="text-sm text-gray-400">-</p>
                        )}
                      </div>
                    </div>

                    {/* QR Codes */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div className="text-center">
                        <p className="text-sm font-medium text-gray-500 mb-2">QR Code Homolog</p>
                        {regressivo.qrCodeHomolog ? (
                          <img 
                            src={regressivo.qrCodeHomolog} 
                            alt="QR Code Homolog" 
                            className="w-24 h-24 mx-auto border rounded"
                          />
                        ) : (
                          <div className="w-24 h-24 mx-auto bg-gray-100 border rounded flex items-center justify-center">
                            <span className="text-xs text-gray-400">Sem QR</span>
                          </div>
                        )}
                      </div>
                      <div className="text-center">
                        <p className="text-sm font-medium text-gray-500 mb-2">QR Code Alpha</p>
                        {regressivo.qrCodeAlpha ? (
                          <img 
                            src={regressivo.qrCodeAlpha} 
                            alt="QR Code Alpha" 
                            className="w-24 h-24 mx-auto border rounded"
                          />
                        ) : (
                          <div className="w-24 h-24 mx-auto bg-gray-100 border rounded flex items-center justify-center">
                            <span className="text-xs text-gray-400">Sem QR</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Action Button */}
                    <div className="flex justify-center">
                      <Link to={`/regressivo/${regressivo.regressivoId}`}>
                        <Button 
                          className="ion-primary"
                          disabled={isExpired}
                        >
                          {isExpired ? 'SLA Vencido - Visualizar' : 'Acessar Testes'}
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

export default QualityDashboard

