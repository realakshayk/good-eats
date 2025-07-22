#!/bin/bash
mkdir -p backups
tar czf backups/env_backup_$(date +%Y%m%d%H%M%S).tar.gz .env* config/.env* prod.env* *.env* 