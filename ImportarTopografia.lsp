(defun c:ImportarUTM ( / archDXF ptIns scl)
  (setq archDXF (getfiled "Seleccione archivo DXF a importar" "" "dxf" 4))
  (if archDXF
    (progn
      (setq ptIns '(0.0 0.0 0.0))
      (setq scl 1.0)
      
      ; Insert the DXF block. En versiones recientes y en español podría ser "-INSERTA"
      (command "_.-INSERT" (strcat "*" archDXF) ptIns scl "")
      
      ; Zoom extents
      (command "_.ZOOM" "_E")
      (princ "\nTopografía importada exitosamente.")
    )
    (princ "\nOperación cancelada.")
  )
  (princ)
)
(princ "\nComando 'ImportarUTM' cargado. Escriba ImportarUTM para empezar.")
(princ)
