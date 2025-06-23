import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Building2, TestTube } from 'lucide-react'

const LoginPage = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    name: '',
    role: ''
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (formData.name && formData.role) {
      onLogin(formData)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center ion-gradient">
      <Card className="w-full max-w-md mx-4">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 rounded-full ion-primary">
              <Building2 className="h-8 w-8 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            Ion Regressivos
          </CardTitle>
          <CardDescription>
            Sistema de Gerenciamento de Testes Regressivos
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nome</Label>
              <Input
                id="name"
                type="text"
                placeholder="Digite seu nome"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="role">Perfil</Label>
              <Select onValueChange={(value) => setFormData({ ...formData, role: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione seu perfil" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">
                    <div className="flex items-center gap-2">
                      <Building2 className="h-4 w-4" />
                      Administrador
                    </div>
                  </SelectItem>
                  <SelectItem value="quality">
                    <div className="flex items-center gap-2">
                      <TestTube className="h-4 w-4" />
                      Time de Qualidade
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <Button 
              type="submit" 
              className="w-full ion-primary hover:opacity-90 transition-opacity"
              disabled={!formData.name || !formData.role}
            >
              Entrar
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default LoginPage

