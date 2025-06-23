import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Plus, 
  Play, 
  Square, 
  Clock, 
  Trash2, 
  FileText, 
  Settings, 
  LogOut,
  Building2,
  Smartphone,
  Monitor
} from 'lucide-react'

const AdminDashboard = ({ user, onLogout }) => {
  const [regressivos, setRegressivos] = useState([])
  const [squadsConfig, setSquadsConfig] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [showReleaseNotesDialog, setShowReleaseNotesDialog] = useState(false)
  const [selectedRegressivo, setSelectedRegressivo] = useState(null)
  const [releaseNotes, setReleaseNotes] = useState('')

  const [newRegressivo, setNewRegressivo] = useState({
    release: '',
    plataforma: '',
    versaoHomolog: '',
    versaoFirebase: '',
    versaoAlpha: '',
    linkPlanoTestes: '',
    tipoRelease: 'Normal',
    squads_selecionadas: []
  })

  useEffect(() => {
    fetchRegressivos()
    fetchSquadsConfig()
  }, [])

  const fetchRegressivos = async () => {
    try {
      // Simular API call - substituir pela URL real do backend
      const response = await fetch('/api/admin/regressivos')
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
          tipoRelease: 'Normal'
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const fetchSquadsConfig = async () => {
    try {
      const response = await fetch('/api/admin/squads-config')
      if (response.ok) {
        const data = await response.json()
        setSquadsConfig(data.data)
      }
    } catch (error) {
      console.error('Erro ao buscar configuração de squads:', error)
      // Dados mock para desenvolvimento
      setSquadsConfig({
        squads: [
          { id: 1, squad: "01 - SQUAD FORMALIZAÇÃO REMOTA", modules: ["ionFormalizacao", "ionWebViewSdk"] },
          { id: 2, squad: "02 - SQUAD CORRETORA ACOMPANHAMENTO DE RV", modules: ["ionCorretoraAcompanhamento"] }
        ]
      })
    }
  }

  const handleCreateRegressivo = async () => {
    try {
      const response = await fetch('/api/admin/regressivos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newRegressivo)
      })
      
      if (response.ok) {
        fetchRegressivos()
        setShowCreateDialog(false)
        setNewRegressivo({
          release: '',
          plataforma: '',
          versaoHomolog: '',
          versaoFirebase: '',
          versaoAlpha: '',
          linkPlanoTestes: '',
          tipoRelease: 'Normal',
          squads_selecionadas: []
        })
      }
    } catch (error) {
      console.error('Erro ao criar regressivo:', error)
    }
  }

  const handleSLAAction = async (regressivoId, action, horas = null) => {
    try {
      let url = `/api/admin/regressivos/${regressivoId}/${action}`
      let body = null
      
      if (action === 'incluir-tempo') {
        body = JSON.stringify({ horas })
      }
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body
      })
      
      if (response.ok) {
        fetchRegressivos()
      }
    } catch (error) {
      console.error(`Erro ao ${action}:`, error)
    }
  }

  const handleDeleteRegressivo = async (regressivoId) => {
    if (confirm('Tem certeza que deseja excluir este regressivo?')) {
      try {
        const response = await fetch(`/api/admin/regressivos/${regressivoId}`, {
          method: 'DELETE'
        })
        
        if (response.ok) {
          fetchRegressivos()
        }
      } catch (error) {
        console.error('Erro ao excluir regressivo:', error)
      }
    }
  }

  const handleGenerateReleaseNotes = async (regressivoId) => {
    try {
      const response = await fetch(`/api/admin/regressivos/${regressivoId}/release-notes`, {
        method: 'POST'
      })
      
      if (response.ok) {
        const data = await response.json()
        setReleaseNotes(data.data.release_notes)
        setSelectedRegressivo(regressivoId)
        setShowReleaseNotesDialog(true)
      }
    } catch (error) {
      console.error('Erro ao gerar release notes:', error)
    }
  }

  const formatDateTime = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString('pt-BR')
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
              <Building2 className="h-8 w-8" />
              <div>
                <h1 className="text-xl font-bold">Painel Administrativo</h1>
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
        {/* Actions */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Regressivos</h2>
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button className="ion-primary">
                <Plus className="h-4 w-4 mr-2" />
                Criar Regressivo
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Criar Novo Regressivo</DialogTitle>
                <DialogDescription>
                  Preencha as informações para criar um novo regressivo
                </DialogDescription>
              </DialogHeader>
              
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="release">Release</Label>
                    <Input
                      id="release"
                      value={newRegressivo.release}
                      onChange={(e) => setNewRegressivo({...newRegressivo, release: e.target.value})}
                      placeholder="Ex: R113"
                    />
                  </div>
                  <div>
                    <Label htmlFor="plataforma">Plataforma</Label>
                    <Select onValueChange={(value) => setNewRegressivo({...newRegressivo, plataforma: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Android">
                          <div className="flex items-center gap-2">
                            <Smartphone className="h-4 w-4" />
                            Android
                          </div>
                        </SelectItem>
                        <SelectItem value="iOS">
                          <div className="flex items-center gap-2">
                            <Smartphone className="h-4 w-4" />
                            iOS
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="versaoHomolog">Versão Homolog</Label>
                    <Input
                      id="versaoHomolog"
                      value={newRegressivo.versaoHomolog}
                      onChange={(e) => setNewRegressivo({...newRegressivo, versaoHomolog: e.target.value})}
                      placeholder="Ex: 2.58.0"
                    />
                  </div>
                  <div>
                    <Label htmlFor="versaoFirebase">Versão Firebase</Label>
                    <Input
                      id="versaoFirebase"
                      value={newRegressivo.versaoFirebase}
                      onChange={(e) => setNewRegressivo({...newRegressivo, versaoFirebase: e.target.value})}
                      placeholder="Ex: 2.58.99"
                    />
                  </div>
                  <div>
                    <Label htmlFor="versaoAlpha">Versão Alpha</Label>
                    <Input
                      id="versaoAlpha"
                      value={newRegressivo.versaoAlpha}
                      onChange={(e) => setNewRegressivo({...newRegressivo, versaoAlpha: e.target.value})}
                      placeholder="Ex: 2.58.1"
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="linkPlanoTestes">Link Plano de Testes</Label>
                  <Input
                    id="linkPlanoTestes"
                    value={newRegressivo.linkPlanoTestes}
                    onChange={(e) => setNewRegressivo({...newRegressivo, linkPlanoTestes: e.target.value})}
                    placeholder="https://..."
                  />
                </div>
                
                <div>
                  <Label htmlFor="tipoRelease">Tipo de Release</Label>
                  <Select onValueChange={(value) => setNewRegressivo({...newRegressivo, tipoRelease: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Normal">Normal</SelectItem>
                      <SelectItem value="Exclusiva">Exclusiva</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                {squadsConfig && (
                  <div>
                    <Label>Squads Participantes</Label>
                    <div className="max-h-40 overflow-y-auto border rounded p-2 space-y-2">
                      {squadsConfig.squads.map((squad) => (
                        <label key={squad.id} className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={newRegressivo.squads_selecionadas.includes(squad.squad)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setNewRegressivo({
                                  ...newRegressivo,
                                  squads_selecionadas: [...newRegressivo.squads_selecionadas, squad.squad]
                                })
                              } else {
                                setNewRegressivo({
                                  ...newRegressivo,
                                  squads_selecionadas: newRegressivo.squads_selecionadas.filter(s => s !== squad.squad)
                                })
                              }
                            }}
                          />
                          <span className="text-sm">{squad.squad}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancelar
                </Button>
                <Button onClick={handleCreateRegressivo} className="ion-primary">
                  Criar Regressivo
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Regressivos List */}
        <div className="grid gap-6">
          {regressivos.map((regressivo) => (
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
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Versão Homolog</p>
                    <p className="text-sm">{regressivo.versaoHomolog}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">Versão Alpha</p>
                    <p className="text-sm">{regressivo.versaoAlpha}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-500">SLA</p>
                    <p className="text-sm">
                      {regressivo.slaInicio ? 
                        `${formatDateTime(regressivo.slaInicio)} - ${formatDateTime(regressivo.slaFim)}` : 
                        'Não iniciado'
                      }
                    </p>
                  </div>
                </div>
                
                <div className="flex flex-wrap gap-2">
                  <Button 
                    size="sm" 
                    onClick={() => handleSLAAction(regressivo.regressivoId, 'iniciar-sla')}
                    disabled={regressivo.slaInicio}
                    className="ion-secondary"
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Iniciar SLA
                  </Button>
                  
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleSLAAction(regressivo.regressivoId, 'parar-sla')}
                    disabled={!regressivo.slaInicio || regressivo.statusGeral === 'finalizado'}
                  >
                    <Square className="h-4 w-4 mr-1" />
                    Parar SLA
                  </Button>
                  
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => {
                      const horas = prompt('Quantas horas adicionar?')
                      if (horas) handleSLAAction(regressivo.regressivoId, 'incluir-tempo', parseInt(horas))
                    }}
                    disabled={!regressivo.slaInicio}
                  >
                    <Clock className="h-4 w-4 mr-1" />
                    Incluir Tempo
                  </Button>
                  
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleGenerateReleaseNotes(regressivo.regressivoId)}
                  >
                    <FileText className="h-4 w-4 mr-1" />
                    Release Notes
                  </Button>
                  
                  <Button 
                    size="sm" 
                    variant="destructive"
                    onClick={() => handleDeleteRegressivo(regressivo.regressivoId)}
                  >
                    <Trash2 className="h-4 w-4 mr-1" />
                    Excluir
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Release Notes Dialog */}
      <Dialog open={showReleaseNotesDialog} onOpenChange={setShowReleaseNotesDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Release Notes Geradas</DialogTitle>
            <DialogDescription>
              Release notes geradas automaticamente com IA Gemini
            </DialogDescription>
          </DialogHeader>
          
          <div className="py-4">
            <Textarea
              value={releaseNotes}
              onChange={(e) => setReleaseNotes(e.target.value)}
              className="min-h-[400px] font-mono text-sm"
              placeholder="Release notes serão geradas aqui..."
            />
          </div>
          
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowReleaseNotesDialog(false)}>
              Fechar
            </Button>
            <Button 
              onClick={() => {
                navigator.clipboard.writeText(releaseNotes)
                alert('Release notes copiadas para a área de transferência!')
              }}
              className="ion-primary"
            >
              Copiar
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default AdminDashboard

