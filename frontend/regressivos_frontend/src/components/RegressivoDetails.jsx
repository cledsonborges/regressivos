import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Progress } from '@/components/ui/progress'
import { 
  ArrowLeft, 
  LogOut, 
  Edit, 
  Save, 
  X, 
  CheckCircle, 
  Clock, 
  XCircle, 
  Bug,
  AlertTriangle,
  Users,
  Package,
  ExternalLink
} from 'lucide-react'

const RegressivoDetails = ({ user, onLogout }) => {
  const { id } = useParams()
  const [regressivo, setRegressivo] = useState(null)
  const [squadsModulos, setSquadsModulos] = useState([])
  const [statusResumo, setStatusResumo] = useState(null)
  const [slaInfo, setSlaInfo] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editingItem, setEditingItem] = useState(null)
  const [editForm, setEditForm] = useState({})

  useEffect(() => {
    fetchRegressivoDetails()
    // Atualizar SLA a cada 30 segundos
    const interval = setInterval(fetchSlaInfo, 30000)
    return () => clearInterval(interval)
  }, [id])

  const fetchRegressivoDetails = async () => {
    try {
      const response = await fetch(`/api/quality/regressivos/${id}`)
      if (response.ok) {
        const data = await response.json()
        setRegressivo(data.data.regressivo)
        setSquadsModulos(data.data.squads_modulos)
        setSlaInfo({
          sla_vencido: data.data.sla_vencido,
          tempo_restante: data.data.tempo_restante
        })
      }
    } catch (error) {
      console.error('Erro ao buscar detalhes:', error)
      // Dados mock para desenvolvimento
      setRegressivo({
        regressivoId: id,
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
      })
      setSquadsModulos([
        {
          squadModuloId: '1',
          squad: '02 - SQUAD CORRETORA ACOMPANHAMENTO DE RV',
          modulo: 'ionCorretoraAcompanhamento-2.3.2',
          detalheEntrega: 'Ajuste de crash ao clicar duas vezes na aba bolsa',
          responsavel: 'Edilson Cordeiro',
          status: 'concluído',
          reportarBug: ''
        },
        {
          squadModuloId: '2',
          squad: '07 - ACOMPAN. CANAIS INVESTIMENTOS PF',
          modulo: 'ionAcompanhamento-v3.3.2',
          detalheEntrega: 'Nada a acrescentar.',
          responsavel: 'Mariah Schevenin',
          status: 'em andamento',
          reportarBug: ''
        }
      ])
      setSlaInfo({
        sla_vencido: false,
        tempo_restante: '23:45:30'
      })
    } finally {
      setLoading(false)
    }
    
    fetchStatusResumo()
  }

  const fetchStatusResumo = async () => {
    try {
      const response = await fetch(`/api/quality/regressivos/${id}/status-resumo`)
      if (response.ok) {
        const data = await response.json()
        setStatusResumo(data.data)
      }
    } catch (error) {
      console.error('Erro ao buscar resumo:', error)
      setStatusResumo({
        total_itens: 2,
        status_count: { 'concluído': 1, 'em andamento': 1, 'bloqueado': 0, 'concluido com bugs': 0 },
        bugs_reportados: 0,
        progresso_percentual: 50
      })
    }
  }

  const fetchSlaInfo = async () => {
    try {
      const response = await fetch(`/api/quality/regressivos/${id}/verificar-sla`)
      if (response.ok) {
        const data = await response.json()
        setSlaInfo(data.data)
      }
    } catch (error) {
      console.error('Erro ao verificar SLA:', error)
    }
  }

  const handleEdit = (item) => {
    setEditingItem(item.squadModuloId)
    setEditForm({
      status: item.status,
      detalheEntrega: item.detalheEntrega,
      responsavel: item.responsavel,
      reportarBug: item.reportarBug
    })
  }

  const handleSave = async (squadModuloId) => {
    try {
      const response = await fetch(`/api/quality/squad-modulo/${squadModuloId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editForm)
      })
      
      if (response.ok) {
        setEditingItem(null)
        fetchRegressivoDetails()
      } else {
        const error = await response.json()
        alert(error.error || 'Erro ao salvar')
      }
    } catch (error) {
      console.error('Erro ao salvar:', error)
      alert('Erro ao salvar alterações')
    }
  }

  const handleCancel = () => {
    setEditingItem(null)
    setEditForm({})
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
        return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusBadge = (status) => {
    const variants = {
      'concluído': 'bg-green-100 text-green-800',
      'em andamento': 'bg-yellow-100 text-yellow-800',
      'bloqueado': 'bg-red-100 text-red-800',
      'concluido com bugs': 'bg-purple-100 text-purple-800'
    }
    return (
      <Badge className={variants[status] || 'bg-gray-100 text-gray-800'}>
        {getStatusIcon(status)}
        <span className="ml-1">{status}</span>
      </Badge>
    )
  }

  const formatDateTime = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString('pt-BR')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!regressivo) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="text-center py-12">
          <CardContent>
            <AlertTriangle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Regressivo não encontrado
            </h3>
            <Link to={user.role === 'admin' ? '/admin' : '/quality'}>
              <Button>Voltar</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  const isExpired = slaInfo?.sla_vencido

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="ion-header shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center gap-3">
              <Link to={user.role === 'admin' ? '/admin' : '/quality'}>
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4" />
                </Button>
              </Link>
              <div>
                <h1 className="text-xl font-bold">
                  {regressivo.release} - {regressivo.plataforma}
                </h1>
                <p className="text-sm opacity-90">Detalhes do Regressivo</p>
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
        {/* SLA Alert */}
        {isExpired && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <h3 className="font-medium text-red-800">SLA Vencido</h3>
            </div>
            <p className="text-red-700 mt-1">
              O prazo para edição dos testes expirou. Os campos estão bloqueados para edição.
            </p>
          </div>
        )}

        {/* SLA Timer */}
        {regressivo.slaInicio && !isExpired && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-blue-800">Tempo Restante do SLA</h3>
                <p className="sla-timer text-blue-600">
                  {slaInfo?.tempo_restante || '00:00:00'}
                </p>
              </div>
              <Clock className="h-8 w-8 text-blue-600" />
            </div>
            <p className="text-blue-700 text-sm mt-1">
              SLA: {formatDateTime(regressivo.slaInicio)} - {formatDateTime(regressivo.slaFim)}
            </p>
          </div>
        )}

        {/* Progress Summary */}
        {statusResumo && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Resumo do Progresso
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">
                    {statusResumo.status_count['concluído'] || 0}
                  </p>
                  <p className="text-sm text-gray-600">Concluídos</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-600">
                    {statusResumo.status_count['em andamento'] || 0}
                  </p>
                  <p className="text-sm text-gray-600">Em Andamento</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">
                    {statusResumo.status_count['bloqueado'] || 0}
                  </p>
                  <p className="text-sm text-gray-600">Bloqueados</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-600">
                    {statusResumo.bugs_reportados || 0}
                  </p>
                  <p className="text-sm text-gray-600">Bugs Reportados</p>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Progresso Geral</span>
                  <span>{statusResumo.progresso_percentual}%</span>
                </div>
                <Progress value={statusResumo.progresso_percentual} className="h-2" />
              </div>
            </CardContent>
          </Card>
        )}

        {/* Release Info */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Informações da Release
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-500">Versão Homolog</p>
                <p className="font-mono">{regressivo.versaoHomolog}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Versão Firebase</p>
                <p className="font-mono">{regressivo.versaoFirebase}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Versão Alpha</p>
                <p className="font-mono">{regressivo.versaoAlpha}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Plano de Testes</p>
                {regressivo.linkPlanoTestes ? (
                  <a 
                    href={regressivo.linkPlanoTestes} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 flex items-center gap-1"
                  >
                    Acessar <ExternalLink className="h-3 w-3" />
                  </a>
                ) : (
                  <p className="text-gray-400">-</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Squads e Módulos */}
        <Card>
          <CardHeader>
            <CardTitle>Squads e Módulos</CardTitle>
            <CardDescription>
              Atualize o status dos testes para cada squad e módulo
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {squadsModulos.map((item) => (
                <div key={item.squadModuloId} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="font-medium text-gray-900">{item.squad}</h4>
                      <p className="text-sm text-gray-600 font-mono">{item.modulo}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(item.status)}
                      {!isExpired && editingItem !== item.squadModuloId && (
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => handleEdit(item)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>

                  {editingItem === item.squadModuloId ? (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="status">Status</Label>
                          <Select 
                            value={editForm.status} 
                            onValueChange={(value) => setEditForm({...editForm, status: value})}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="em andamento">Em Andamento</SelectItem>
                              <SelectItem value="concluído">Concluído</SelectItem>
                              <SelectItem value="bloqueado">Bloqueado</SelectItem>
                              <SelectItem value="concluido com bugs">Concluído com Bugs</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label htmlFor="responsavel">Responsável</Label>
                          <Input
                            id="responsavel"
                            value={editForm.responsavel}
                            onChange={(e) => setEditForm({...editForm, responsavel: e.target.value})}
                            placeholder="Nome do responsável"
                          />
                        </div>
                      </div>
                      
                      <div>
                        <Label htmlFor="detalheEntrega">Detalhe da Entrega</Label>
                        <Textarea
                          id="detalheEntrega"
                          value={editForm.detalheEntrega}
                          onChange={(e) => setEditForm({...editForm, detalheEntrega: e.target.value})}
                          placeholder="Descreva os detalhes da entrega..."
                          rows={3}
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="reportarBug">Reportar Bug</Label>
                        <Textarea
                          id="reportarBug"
                          value={editForm.reportarBug}
                          onChange={(e) => setEditForm({...editForm, reportarBug: e.target.value})}
                          placeholder="Descreva o bug encontrado (se houver)..."
                          rows={3}
                        />
                      </div>
                      
                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          onClick={() => handleSave(item.squadModuloId)}
                          className="ion-primary"
                        >
                          <Save className="h-4 w-4 mr-1" />
                          Salvar
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={handleCancel}
                        >
                          <X className="h-4 w-4 mr-1" />
                          Cancelar
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div>
                        <p className="text-sm font-medium text-gray-500">Responsável</p>
                        <p className="text-sm">{item.responsavel || '-'}</p>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-500">Detalhe da Entrega</p>
                        <p className="text-sm">{item.detalheEntrega || '-'}</p>
                      </div>
                      {item.reportarBug && (
                        <div>
                          <p className="text-sm font-medium text-gray-500 flex items-center gap-1">
                            <Bug className="h-4 w-4 text-red-600" />
                            Bug Reportado
                          </p>
                          <p className="text-sm text-red-700 bg-red-50 p-2 rounded">
                            {item.reportarBug}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default RegressivoDetails

